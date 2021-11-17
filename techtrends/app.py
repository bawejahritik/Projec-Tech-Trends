import logging
import sqlite3
import sys
from datetime import datetime
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

logger = logging.getLogger("__name__")
logging.basicConfig(level=logging.DEBUG)
h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.DEBUG)
h2 = logging.StreamHandler(sys.stderr)
h2.setLevel(logging.ERROR)
logger.addHandler(h1)
logger.addHandler(h2)

# Function to get a database connection.
# This function connects to database with the name `database.db`
total_connections = 0
def get_db_connection():
    global  total_connections
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    total_connections += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logging.info('%s, %s, Article doesn\'t exist', datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M:%S"))
        return render_template('404.html'), 404
    else:
        logging.info('%s, %s, Article "%s" retrieved!', datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M:%S")
                     ,post['title'])
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('%s, %s, About Us retrieved!', datetime.now().strftime("%d/%m/%Y"),
                 datetime.now().strftime("%H:%M:%S"))
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.info('%s, %s, Article "%s" created!', datetime.now().strftime("%d/%m/%Y"),
                         datetime.now().strftime("%H:%M:%S"), title)
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthz():
    res = app.response_class(status=200, response=json.dumps({"result": "OK - healthy"}))
    return res

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    total_post = connection.execute('SELECT * FROM posts').fetchall()
    no_of_posts = len(total_post)
    connection.close()
    res = app.response_class(status=200, mimetype='application/json',
                             response=json.dumps({"db_connection_count": total_connections, "post_count": no_of_posts}))
    return res

# start the application on port 3111
if __name__ == "__main__":
    # logging.basicConfig(filename='app.log', level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
