# Import Flask
from flask import Flask, render_template, request, url_for, redirect
import json, os

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

@app.route('/submit_post', methods=['POST'])
def submit_post():
    code_name = request.form['code_name']
    post_content = request.form['post_content']
    post_date = datafunctions.get_pst_time()
    post_colour = request.form['post_colours']

    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
        posts = all_posts["all_posts"]
        post_id = all_posts["post_increments"]

    all_posts["post_increments"] += 1

    this_post = {
        "code_name": code_name,
        "content": post_content,
        "date_posted": post_date,
        "post_id": post_id,
        "colour": post_colour
    }

    posts.append(this_post)

    with open('posts.json', 'w') as file:
        json.dump(all_posts, file, indent=4)
    file.close()

    return redirect(url_for('index'))
    #return render_template("index.html", post_data=all_posts)


# Application routes
@app.route("/") # / means index, it's the homepage.
def index(): # You can name your function whatever you want.
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
        posts = all_posts["all_posts"]
    file.close()

    return render_template("index.html", post_data=all_posts)



app.run(
  host = "0.0.0.0", # or 127.0.0.1 (DONT USE LOCALHOST)
  port = 8080,
  debug = True
)