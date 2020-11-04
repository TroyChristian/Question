from flask import Flask, render_template, g, request , session, redirect, url_for
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db' ):
		g.sqlite_db.close() 

def get_current_user():
	user = None #local variable
	
	if 'user' in session.keys(): #if user key in session 
		user = session['user'] #ie "admin"
		db = get_db() 
		user_cursor = db.execute('SELECT id, name, password, expert, admin FROM users WHERE name = ?', [user])
		user_result = user_cursor.fetchone() 
		return user_result #record from the database




@app.route('/home')
@app.route('/')
def index():

	user = get_current_user()


	return render_template('home.html', user=user)

@app.route('/register', methods=['GET','POST'])
def register():
	user = get_current_user()
	if request.method == 'POST':
		db = get_db()
		hashed_password = generate_password_hash(request.form['password'], method='sha256')
		db.execute('insert into users (name, password, expert, admin) values (?,?,?,?)', [request.form['name'], hashed_password, '0','0'])
		db.commit() 
		session['user'] = request.form["name"]
		print("succesfully added user")
		return redirect(url_for('index'))
	return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
	


	user = get_current_user()
	if request.method == "POST":
		name = request.form['name']
		password = request.form['password']
		db = get_db()
		user_cursor = db.execute("SELECT id, name, password FROM users WHERE name = ?", [name])
		user_result = user_cursor.fetchone()
		if check_password_hash(user_result["password"], password):
			session['user'] = user_result['name']
			
			return redirect(url_for('index'))
		else:
			return "<h6> The password is incorrect </h6>"
	return render_template('login.html')

@app.route('/question')
def question():
	user = get_current_user()
	return render_template('question.html',user=user)

@app.route('/answer')
def answer():
	user = get_current_user()
	return render_template('answer.html',user=user)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
	if request.method == 'POST':
		print(request.method)
		return "<h6>Question: {}, expert id: {} </h6>".format(request.form['question'], request.form['expert'])
	user = get_current_user()
	

	# Get experts to populate experts form selection
	db = get_db()
	experts_cur = db.execute("SELECT id, name from users WHERE expert = 1")
	expert_rows = experts_cur.fetchall() # results in list of sql lite row objects
	
	

	print(request.method)
	return render_template('ask.html',user=user, experts=expert_rows)

@app.route('/unanswered')
def unanswered():
	user = get_current_user()
	return render_template('unanswered.html',user=user)

@app.route('/users')
def users():
	user = get_current_user()
	db = get_db()
	users_cursor = db.execute('SELECT id, name, expert, admin FROM users') 
	users_results = users_cursor.fetchall() # list of users sqlite row object
	

	return render_template('users.html',user=user, users=users_results)

@app.route('/logout')
def logout():
	session.pop('user', None) #removes (and returns) the key. Second arg is returned if key not found
	return redirect(url_for('index'))

@app.route('/promote<user_id>') #user id passed in url and to promote func
def promote(user_id):
	db = get_db() # grab a cursor
	#Check if user is already an expert
	expert_cur = db.execute('SELECT expert FROM users WHERE id = ?', [user_id]) 
	is_expert = expert_cur.fetchone() # Results in a  sqlite Row object behaves like a  tuple
	


	if is_expert["expert"] == 1:
		user_cursor = db.execute('UPDATE users SET expert = 0 WHERE id = ?', [user_id])
		print("User demoted and is no longer an expert")
		db.commit()
		return redirect(url_for('users'))
	

	user_cursor = db.execute('UPDATE users SET expert = 1 WHERE id = ?', [user_id])
	print("User promoted to expert")
	db.commit()
	return redirect(url_for('users'))




if __name__ == '__main__':
	app.run(debug=True)