# Import Flask
from flask import Flask, render_template, request, url_for, redirect
import json, os, random
from flask_wtf import FlaskForm
from wtforms import StringField, validators, TextAreaField, RadioField, ValidationError
from wtforms.validators import DataRequired, Length, InputRequired
from better_profanity import profanity


# MongoDB
import dns # For mongodb to work, this installs an older version of bson, if version error, uninstall bson/pymongo to get it working again
import pymongo
from pymongo import MongoClient
import os
# MongoDB ^^^


mongo_password = os.environ['mongo_password'] # Virtual Env Variable

client = pymongo.MongoClient("mongodb+srv://DonaldKL:"+ mongo_password +"@cluster0.r5ghf.mongodb.net/Quillity?retryWrites=true&w=majority")
db = client.Quillity


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

# If you make a custom validation, go to the HTML file and also make it display the error message
def profanity_check(form, field):
    if profanity.contains_profanity(field.data):
        raise ValidationError("Profanity was detected in your " + str(field.label) + "!")
def check_tag_limit(form, field):
    if len(field.data.split(" ")) > 5:
        raise ValidationError("You can only add a maximum of 5 tags!")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

class post_form(FlaskForm):
    post_alias = StringField('alias',[validators.Length(min=2, max=15, message="Must be between 2-15 characters!"), profanity_check])
    post_content = TextAreaField('post',[validators.Length(min=10, max=150, message="Must be between 10-150 characters!"), profanity_check],render_kw={"rows": 4, "cols": 50})
    colours = RadioField('', choices=[('#FFFF88','Yellow'),('#ff7eb9','Pink'),('#7afcff', 'Light blue'),('#52f769','Green'),('#E6E6FA','Lavender'),('#FFA500','Orange')], validators=[InputRequired()])
    tags = StringField('tags',[validators.DataRequired(message="You must enter in at least 1 tag"), profanity_check, check_tag_limit])

class comment_form(FlaskForm):
    comment_alias = StringField('alias',[InputRequired(), profanity_check])
    comment_content = TextAreaField('post',[InputRequired(), profanity_check],render_kw={"rows": 4, "cols": 50})
    post_id = StringField('id', validators=[InputRequired()])

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = post_form() 

    code_name = profanity.censor(form.post_alias.data.strip(" "))
    post_content = profanity.censor(form.post_content.data.strip(" "))
    tags = profanity.censor(form.tags.data.strip(" ")).split(" ")

    if form.validate_on_submit():
        code_name = code_name
        post_content = post_content
        post_date = datafunctions.get_pst_time()
        post_colour = form.colours.data

        for increment in db.increments.find({'type': "post_increments"}):
            post_id = increment['post_increments']
            new_post_increment = int(post_id) + random.randint(1,50)
            db.increments.update_one({'type': "post_increments"}, {'$set': {'post_increments': new_post_increment}})

        this_post = {
            "code_name": code_name,
            "content": post_content,
            "date_posted": post_date,
            "post_id": new_post_increment,
            "colour": post_colour,
            "comments": [],
            "tags":tags
        }
    
        db.posts.insert_one(this_post)

        return redirect(url_for('post', post_number = new_post_increment))

    posts_json_data = db.posts.find()
    return render_template("index.html", post_data=posts_json_data, form=form, comment=comment_form())

@app.route('/comment', methods=['GET','POST'])
def post_comment():

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

        for doc in db.posts.find({'post_id': int(post_id)}):
            if len(doc) > 0:
                db.posts.update_one({'post_id': int(post_id)},{'$push': {'comments': comment}})

        return redirect(url_for('post', post_number = str(post_id)))
    
    else:
        post_id = form.post_id.data
        return redirect(url_for('post', post_number = str(post_id)))

# Application routes
@app.route("/") # / means index, it's the homepage.
def index(): # You can name your function whatever you want.

    posts_json_data = db.posts.find() # Gets all the objects in the posts database
 
    return render_template("index.html", post_data=posts_json_data, form=post_form(), comment=comment_form())

@app.route('/post/<post_number>')
def post(post_number):
    foundpost = False

    for thatpost in db.posts.find({'post_id': int(post_number)}):
        if len(thatpost) > 0:
            foundpost = True

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
    for increment in db.increments.find({'type': "room_increments"}):
        beginning = increment['beginning']
        new_beginning = int(beginning) + random.randint(1,99)
        db.increments.update_one({'type': "room_increments"}, {'$set': {'beginning': new_beginning}})

    form = makeroom_form()

    if form.validate_on_submit():
        title = profanity.censor(form.title.data.strip(" "))
        description = profanity.censor(form.description.data.strip(" "))
        created_date = datafunctions.get_pst_time()

        room_id = str(new_beginning) + datafunctions.random_char(4)

        room = {
            "title": title,
            "description": description,
            "date_posted": created_date,
            "room_id": room_id,
            "room_post_increments":0,
            'posts':[],
        }

        db.rooms.insert_one(room)

        return redirect(url_for('room', room_id = room_id))

    else:
        return render_template("makeroom.html", form=form)

@app.route('/room/<room_id>')
def room(room_id):
    form = room_post_form()
    foundroom = False

    for thatroom in db.rooms.find({'room_id': str(room_id)}):
        if len(thatroom) > 0:
            foundroom = True

    if foundroom:
        return render_template("room.html", room_data=thatroom, form = form)
    else:
        return redirect(url_for('index'))



class room_post_form(FlaskForm):
    room_post_alias = StringField('alias',[validators.Length(min=2, max=15, message="Must be between 2-15 characters!"), profanity_check])
    room_post_content = TextAreaField('post',[validators.Length(min=10, max=150, message="Must be between 10-150 characters!"), profanity_check],render_kw={"rows": 4, "cols": 50})
    room_colours = RadioField('', choices=[('#FFFF88','Yellow'),('#ff7eb9','Pink'),('#7afcff', 'Light blue'),('#52f769','Green'),('#E6E6FA','Lavender'),('#FFA500','Orange')], validators=[InputRequired()])
    room_tags = StringField('tags',[validators.DataRequired(message="You must enter in at least 1 tag"), profanity_check, check_tag_limit])
    room_id = StringField('id', validators=[InputRequired()])

@app.route('/room_post', methods=['GET', 'POST']) # Create a post in a room
def room_post():
    form = room_post_form() 

    if form.validate_on_submit():
        code_name = profanity.censor(form.room_post_alias.data.strip(" "))
        post_content = profanity.censor(form.room_post_content.data.strip(" "))
        post_date = datafunctions.get_pst_time()
        post_colour = form.room_colours.data
        room_id = form.room_id.data.strip(" ")
        tags = profanity.censor(form.room_tags.data.strip(" ")).split(" ")

        for thatroom in db.rooms.find({'room_id': str(room_id)}):
            room_post_increment = thatroom["room_post_increments"]
            room_post_id = int(room_post_increment) + random.randint(1,50)
            db.rooms.update_one({'room_id': str(room_id)}, {'$set': {'room_post_increments': room_post_id}})

        this_post = {
            "code_name": code_name,
            "content": post_content,
            "date_posted": post_date,
            "room_post_id": room_post_id,
            "colour": post_colour,
            "comments": [],
            "tags": tags
        }

        for thatroom in db.rooms.find({'room_id': str(room_id)}):
            db.rooms.update_one({'room_id': str(room_id)},{'$push': {'posts': this_post}})

        return redirect(url_for('roompost', room_id = room_id, post_id = room_post_id))
    
    else: # If form cannot validate, bring them back to the room
        room_id = form.room_id.data.strip(" ")
        for thatroom in db.rooms.find({'room_id': str(room_id)}):
            return render_template("room.html", room_data=thatroom, form = form)

@app.route('/roompost/<room_id>/<post_id>')
def roompost(room_id, post_id):
    foundpost = False

    for thatroom in db.rooms.find({'room_id': str(room_id)}):
        for post in thatroom["posts"]:
            if int(post['room_post_id']) == int(post_id):
                thatpost = post
                foundpost = True

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
        
        db.rooms.update_one(
            {'room_id': str(room_id), "posts.room_post_id":int(post_id)},
            { "$push": 
                {"posts.$.comments": comment
                }
            }
        )
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