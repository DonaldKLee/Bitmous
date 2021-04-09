# Import Flask
from flask import Flask, render_template, request, url_for, redirect, flash
import json, os

from flask_wtf import FlaskForm
from wtforms import StringField, validators, TextAreaField, RadioField, ValidationError
from wtforms.validators import DataRequired, Length, InputRequired

from better_profanity import profanity

# Python files
import datafunctions

# Next up, we need to make a Flask app.
# This will allow us to create routes, etc.
app = Flask(__name__) # I put __name__ here, but you can also place any string you want.

# Prevents cache from using the old css file, makes it use the updated one
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
# ^ ^ ^

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

def profanity_check(form, field):
    if profanity.contains_profanity(field.data):
        raise ValidationError("Profanity was detected in your " + str(field.label) + "!")


class post_form(FlaskForm):
    post_alias = StringField('alias',[validators.Length(min=2, max=15, message="Must be between 2-15 characters!"), profanity_check])
    post_content = TextAreaField('post',[validators.Length(min=10, max=150, message="Must be between 10-150 characters!"), profanity_check],render_kw={"rows": 4, "cols": 50})
    colours = RadioField('', choices=[('#FFFF88','Yellow'),('#ff7eb9','Pink'),('#7afcff', 'Light blue'),('#52f769','Green'),('#E6E6FA','Lavender'),('#FFA500','Orange')], validators=[InputRequired()])

class comment_form(FlaskForm):
    comment_alias = StringField('alias',[validators.Length(min=2, max=15, message="Must be between 2-15 characters!"), profanity_check])
    comment_content = TextAreaField('post',[validators.Length(min=10, max=150, message="Must be between 10-150 characters!"), profanity_check],render_kw={"rows": 4, "cols": 50})
    post_id = StringField('id', validators=[InputRequired()])

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
    file.close()
    form = post_form() 

    code_name = profanity.censor(form.post_alias.data.strip(" "))
    post_content = profanity.censor(form.post_content.data.strip(" "))

    if form.validate_on_submit():
        code_name = code_name
        post_content = post_content
        post_date = datafunctions.get_pst_time()
        post_colour = form.colours.data
        with open('posts.json', 'r') as file:
            all_posts = json.load(file)
            posts = all_posts["all_posts"]
            post_id = all_posts["post_increments"]
        file.close()

        all_posts["post_increments"] += 1
        this_post = {
            "code_name": code_name,
            "content": post_content,
            "date_posted": post_date,
            "post_id": post_id,
            "colour": post_colour,
            "comments": []
        }

        posts.append(this_post)
        with open('posts.json', 'w') as file:
            json.dump(all_posts, file, indent=4)
        file.close()

        flash(f"You just changed your name to: { code_name }, you posted { post_content }")
        return redirect(url_for('index'))

    return render_template("index.html", post_data=all_posts, form=form, comment=comment_form())

@app.route('/comment', methods=['GET','POST'])
def post_comment():
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
        posts = all_posts["all_posts"]

    file.close()

    form = comment_form()
    
    if form.validate_on_submit():
        code_name = profanity.censor(form.comment_alias.data.strip(" "))
        post_content = profanity.censor(form.comment_content.data.strip(" "))
        post_date = datafunctions.get_pst_time()

        post_id = form.post_id.data

        comment = {
            "code_name": code_name,
            "content": post_content,
            "date_posted": post_date,
        }

        for post in posts:
            if str(post_id) == str(post["post_id"]):
                post["comments"].append(comment)

        with open('posts.json', 'w') as file:
            json.dump(all_posts, file, indent=4)

        file.close()
        
        return redirect(url_for('index') + "#post" + post_id)
    
    else:
        post_id = form.post_id.data
        return render_template("index.html", anchor=post_id, post_data=all_posts, form=post_form(), comment=comment_form())

# Application routes
@app.route("/") # / means index, it's the homepage.
def index(): # You can name your function whatever you want.
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
        posts = all_posts["all_posts"]
    file.close()

    return render_template("index.html", post_data=all_posts, form=post_form(), comment=comment_form())



app.run(
  host = "0.0.0.0", # or 127.0.0.1 (DONT USE LOCALHOST)
  port = 8080,
  debug = True
)