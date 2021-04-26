# Import Flask
from flask import Flask, render_template, request, url_for, redirect
import json, os, random

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

class post_form(FlaskForm):
    post_alias = StringField('alias',[validators.Length(min=2, max=15, message="Must be between 2-15 characters!"), profanity_check])
    post_content = TextAreaField('post',[validators.Length(min=10, max=150, message="Must be between 10-150 characters!"), profanity_check],render_kw={"rows": 4, "cols": 50})
    colours = RadioField('', choices=[('#FFFF88','Yellow'),('#ff7eb9','Pink'),('#7afcff', 'Light blue'),('#52f769','Green'),('#E6E6FA','Lavender'),('#FFA500','Orange')], validators=[InputRequired()])

class comment_form(FlaskForm):
    comment_alias = StringField('alias',[profanity_check])
    comment_content = TextAreaField('post',[profanity_check],render_kw={"rows": 4, "cols": 50})
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

        all_posts["post_increments"] += random.randint(1,50)
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

        return redirect(url_for('post', post_number = post_id))

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
        
        return redirect(url_for('post', post_number = str(post_id)))
    
    else:
        post_id = form.post_id.data
        return redirect(url_for('post', post_number = str(post_id)))

# Application routes
@app.route("/") # / means index, it's the homepage.
def index(): # You can name your function whatever you want.
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
        posts = all_posts["all_posts"]
    file.close()

    return render_template("index.html", post_data=all_posts, form=post_form(), comment=comment_form())

@app.route('/post/<post_number>')
def post(post_number):
    foundpost = False
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
        posts = all_posts["all_posts"]
    
    for post in posts:
        if str(post_number) == str(post["post_id"]):
            thatpost = post
            foundpost = True
    file.close()

    if foundpost:
        return render_template("post.html", post_data=thatpost, commentform=comment_form())
    else:
        return redirect(url_for('index'))

class makeroom_form(FlaskForm):
    title = StringField('alias',[validators.Length(min=2, max=50, message="Title must be between 2-50 characters!"), profanity_check])
    description = TextAreaField('post',[validators.Length(min=10, max=150, message="Description must be between 10-150 characters!"), profanity_check],render_kw={"rows": 4, "cols": 50}) 

@app.route('/makeroom')
def makeroom():
    form = makeroom_form()
    return render_template("makeroom.html", form=form)

@app.route('/makeroom', methods=['GET','POST'])
def create_room():
    with open('rooms.json', 'r') as file:
        all_rooms = json.load(file)
        rooms = all_rooms["all_rooms"]
        beginning = all_rooms["beginning"]

    all_rooms["beginning"] += random.randint(1,50)
    file.close()
    form = makeroom_form()

    if form.validate_on_submit():
        title = profanity.censor(form.title.data.strip(" "))
        description = profanity.censor(form.description.data.strip(" "))
        created_date = datafunctions.get_pst_time()

        room_id = str(beginning) + datafunctions.random_char(4)

        room = {
            "title": title,
            "description": description,
            "date_posted": created_date,
            "room_id": room_id,
            "room_post_increments":0,
            'posts':[],
        }

        all_rooms["all_rooms"].append(room)

        with open('rooms.json', 'w') as file:
            json.dump(all_rooms, file, indent=4)

        file.close()
        return redirect(url_for('room', room_id = room_id))
    else:
        return render_template("makeroom.html", form=form)


@app.route('/room/<room_id>')
def room(room_id):
    form = room_post_form()
    foundroom = False
    with open('rooms.json', 'r') as file:
        all_rooms = json.load(file)
        rooms = all_rooms["all_rooms"]
    
    for room in rooms:
        if str(room_id) == str(room["room_id"]):
            thatroom = room
            foundroom = True

    file.close()

    if foundroom:
        return render_template("room.html", room_data=thatroom, form = form)
    else:
        return redirect(url_for('index'))

class room_post_form(FlaskForm):
    room_post_alias = StringField('alias',[validators.Length(min=2, max=15, message="Must be between 2-15 characters!"), profanity_check])
    room_post_content = TextAreaField('post',[validators.Length(min=10, max=150, message="Must be between 10-150 characters!"), profanity_check],render_kw={"rows": 4, "cols": 50})
    room_colours = RadioField('', choices=[('#FFFF88','Yellow'),('#ff7eb9','Pink'),('#7afcff', 'Light blue'),('#52f769','Green'),('#E6E6FA','Lavender'),('#FFA500','Orange')], validators=[InputRequired()])
    room_id = StringField('id', validators=[InputRequired()])

@app.route('/room_post', methods=['GET', 'POST']) # Create a post in a room
def room_post():
    with open('rooms.json', 'r') as file:
        all_rooms = json.load(file)

    file.close()
    form = room_post_form() 


    if form.validate_on_submit():
        code_name = profanity.censor(form.room_post_alias.data.strip(" "))
        post_content = profanity.censor(form.room_post_content.data.strip(" "))
        post_date = datafunctions.get_pst_time()
        post_colour = form.room_colours.data
        room_id = form.room_id.data.strip(" ")

        with open('rooms.json', 'r') as file:
            all_rooms = json.load(file)
            rooms = all_rooms["all_rooms"]
        
        for room in rooms:
            if str(room_id) == str(room["room_id"]):
                room_post_id = room['room_post_increments']
                room['room_post_increments'] += random.randint(1,50)

        file.close()

        this_post = {
            "code_name": code_name,
            "content": post_content,
            "date_posted": post_date,
            "room_post_id": room_post_id,
            "colour": post_colour,
            "comments": []
        }

        for post in all_rooms['all_rooms']:
            if str(room_id) == str(post["room_id"]):
                post["posts"].append(this_post)

        with open('rooms.json', 'w') as file:
            json.dump(all_rooms, file, indent=4)
            
        file.close()

        return redirect(url_for('room', room_id = room_id))
    
    else:
        return redirect(url_for('index'))

@app.route('/roompost/<room_id>/<post_id>')
def roompost(room_id, post_id):
    foundpost = False

    with open('rooms.json', 'r') as file:
        all_rooms = json.load(file)
        rooms = all_rooms["all_rooms"]
    
    for room in rooms:
        if str(room_id) == str(room["room_id"]):
            thatroom = room
            for post in thatroom["posts"]:
                if str(post_id) == str(post["room_post_id"]):
                    thatpost = post
                    foundpost = True

    file.close()

    if foundpost:
        return render_template("roompost.html", post_data=thatpost, room_id=room_id, post_id=post_id, commentform=roomcomment_form())
    else:
        return redirect(url_for('room', room_id=room_id, post_id=post_id))

class roomcomment_form(FlaskForm):
    comment_alias = StringField('alias',[profanity_check])
    comment_content = TextAreaField('post',[profanity_check],render_kw={"rows": 4, "cols": 50})
    room_id = StringField('room_id', validators=[InputRequired()])
    post_id = StringField('post_id', validators=[InputRequired()])


@app.route('/roomcomment', methods=['GET','POST'])
def post_room_comment():
    with open('rooms.json', 'r') as file:
        all_rooms = json.load(file)
        rooms = all_rooms["all_rooms"]

    file.close()
    form = roomcomment_form()
    
    if form.validate_on_submit():
        code_name = profanity.censor(form.comment_alias.data.strip(" "))
        post_content = profanity.censor(form.comment_content.data.strip(" "))
        post_date = datafunctions.get_pst_time()
        
        room_id = form.room_id.data
        post_id = form.post_id.data

        comment = {
            "code_name": code_name,
            "content": post_content,
            "date_posted": post_date,
        }

        for room in rooms:
            if str(room_id) == str(room["room_id"]):
                for post in room["posts"]:
                    if str(post_id) == str(post["room_post_id"]):
                        post["comments"].append(comment)

        with open('rooms.json', 'w') as file:
            json.dump(all_rooms, file, indent=4)

        file.close()
        
        return redirect(url_for('roompost', room_id = str(room_id), post_id=str(post_id)))
    
    else:
        room_id = form.room_id.data
        post_id = form.post_id.data
        return redirect(url_for('roompost', room_id = str(room_id), post_id=str(post_id)))

app.run(
  host = "0.0.0.0", # or 127.0.0.1 (DONT USE LOCALHOST)
  port = 8080,
  debug = True
)