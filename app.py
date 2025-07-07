from flask import Flask, render_template, request, current_app, g, session, redirect, url_for, flash
from databse import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) 

def get_currect_user():
   user_result = None
   if 'user' in session:
      user = session['user']

      print("User from session:", user) 
     

      db = get_db()
      user_current = db.execute('select id, name, password, expert, admin from users where name = ?', (user,))
      user_result = user_current.fetchone()
      print("User from session:", user) 
   return user_result


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('sqlite_db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
       db.executescript(f.read().decode('utf-8'))

@app.route('/')
def index():
   user = get_currect_user()
   questions = None

   if user: 
      db = get_db()
      questions = db.execute('select questions.question_text as question_text, questions.answer_text as answer_text, questions.id as id, users.name as name, users.expert as expert_id from questions join users on users.id = questions.answer_by_id  where answer_text is not null and expert_id = ?', [user['id']]).fetchall()
   return render_template('home.html', user=user, questions=questions)



@app.route('/register', methods=['GET','POST'])
def register():
   user = get_currect_user()
   if user:
      return redirect(url_for('index'))
   if request.method == 'POST':
      hash_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
      db = get_db()
      print(db)
      db.execute('insert into users (name, password, expert, admin) values (?,?,?,?)', [request.form['name'], hash_password, '1', '1'])
      db.commit()
      session['user'] = request.form['name']
      user = get_currect_user()

      return redirect(url_for('index'))
   return render_template('register.html',  user=user)

@app.route('/login', methods=['GET','POST'])
def login():
   user = get_currect_user()
   if request.method == "POST":
      db = get_db()

      name = request.form['name']
      password = request.form['password']
      user_curr = db.execute('SELECT id, name, password FROM users WHERE name = ?',(name,))
      user_result = user_curr.fetchone()

      if user_result and check_password_hash(user_result['password'], password):
         session['user'] = user_result['name']
         return redirect(url_for('index'))

   return render_template('login.html', user=user)

@app.route('/question/<question_id>')
def question(question_id):
   user = get_currect_user()
   question = None
   if user:
      db = get_db()
      question = db.execute('select questions.question_text as question_text, questions.answer_text as answer_text, questions.id as id, users.name as name, users.expert as expert_id from questions join users on users.id = questions.answer_by_id  where answer_text is not null and questions.id = ?', [question_id]).fetchone()
   return render_template('question.html', user=user, question=question)

@app.route('/answer/<question_id>', methods=['GET','POST'])
def answer(question_id):
   user = get_currect_user()
   question = None
   if user:
      db = get_db()
      if request.method == 'POST':
       db.execute('update questions  set answer_text = ? where id = ? ', [request.form['answer'], question_id])
       db.commit()
       return redirect(url_for('index'))
      question = db.execute('select question_text, id, answer_by_id, expert_id from questions where id = ? ', [question_id]).fetchone()
   return render_template('answer.html', user=user, question=question)

@app.route('/unanswered')
def unanswered():
   user =  get_currect_user()
   questions = None

   if user: 
      db = get_db()
      questions = db.execute('select questions.question_text, questions.id as id, users.name as name, questions.expert_id from questions join users on users.id  = questions.answer_by_id where questions.answer_text is null and questions.expert_id = ?', [user['id']]).fetchall()
   return render_template('unanswered.html', user=user, questions=questions)

@app.route('/ask', methods=['GET','POST'])
def ask():
   user =  get_currect_user()  
   if user:
    db = get_db()
    if request.method == 'POST':
        db.execute('insert into questions (question_text, answer_by_id, expert_id) values (?,?,?)', [request.form['question'], user['id'], request.form['expert']] )
        db.commit()
        return redirect(url_for('index'))
    experts = db.execute('select id, name from users where expert = 1')
    experts_result  = experts.fetchall()
    return render_template('ask.html', user=user, experts=experts_result)
   return render_template('ask.html', user=user)


@app.route('/users')
def users():
   user =  get_currect_user()
   if user:
      db = get_db()
      users = db.execute('select id, name, admin, expert from users')
      users_result = users.fetchall()
   return render_template('users.html', user=user, users=users_result)

@app.route('/logout')
def logout():
   session.pop('user', None)
   return redirect(url_for('index'))

@app.route('/promote/<user_id>')
def promote(user_id):
   print("user id", user_id)

   user = get_currect_user()
   if user:
      db = get_db()
      db.execute('update users set expert = 1 where id = ?', [user_id])
      db.commit()
      redirect(url_for('users'))

   return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
    