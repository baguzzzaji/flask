# Controller
from flask import Flask, render_template, request, session, \
        flash, redirect, url_for, g
from functools import wraps
import sqlite3


# Configuration
DATABASE = 'blog.db'
app = Flask(__name__)
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = "BS\x87Ax\xe3\xe2\xa2v\xee\x8bT9\x19\x89\xd9\x83\xe3\xdel\xf5\xc1$Z" # os.urandom(24)

# Pulls in app configuration by looking for UPPERCASE variable
app.config.from_object(__name__)

# Function used for connecting to the database
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('login'))
	return wrap

@app.route('/', methods=['GET', 'POST'])
def login():	
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid credentials. Please try again.'
		else:
			session['logged_in'] = True
			return redirect(url_for('main'))		

	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('login'))
	
@app.route('/main')
@login_required
def main():
	g.db = connect_db()
	cur  = g.db.execute('select * from posts')
	posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]
	g.db.close
	return render_template('main.html', posts=posts)

@app.route('/add', methods=['POST'])
@login_required
def add():
	title = request.form['title']
	post = request.form['post']
	if not title or not post:
		flash('All fields are required. Please try again.')
		return redirect(url_for('main'))
	else:
		g.db = connect_db()
		g.db.execute('insert into posts (title, post) values (?,?)', [request.form['title'], request.form['post']])
		g.db.commit()
		g.db.close()
		flash('New entry was successfully posted!')
		return redirect(url_for('main'))
		
if __name__ == '__main__':
    app.run(debug=True)

