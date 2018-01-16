from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Blogzz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, password):
        self.name = name
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

def get_blog():

    return Blog.query.all()

def get_users():
    return Person.query.all()

def get_user_id():
    return Person.query.filter_by(name = session['user']).first()

def get_user_name():
    return Blog.query.filter_by(owner_id=get_user_id().id).all()

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/")

@app.route('/', methods=['POST', 'GET'])
def blog_users():
    
    return render_template('home.html',users=get_users())
@app.route("/signup", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        name = request.form['name']
        password = request.form['password']
        verify = request.form['verify']
        if password != verify:
            flash('Passwords does not match')
            return redirect('/signup')
        elif Person.query.filter_by(name=name).first():
            flash('This email already exist try another one')
            return redirect('/signup')            
        user = Person(name=name, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.name
        return redirect("/blog/newpost")
    else:
        return render_template('signup.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        name = request.form['name']
        password = request.form['password']
        user = Person.query.filter_by(name=name).first()
        if user and user.password==password:
            session['user'] = user.name
            return redirect("/blog/newpost")
    else:
        return render_template('login.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog_fun():
    return render_template('blog.html',blog_c=get_blog())

@app.route('/blog/newpost', methods=['POST', 'GET'])
def new_entry():

    if 'user' not in session:
        return redirect("/login")
    else:
        Current_id = Person.query.filter_by(name= session['user']).first().id

        if request.method == 'POST':
            
            title = request.form['title']
            body = request.form['body']
            owner_id = Current_id
        
            if not title:
                error = "Enter title for your blog"
                return render_template('/new.html', error = error )
            elif not body:
                error = "Enter body for your blog"
                return render_template('/new.html', error = error )         
            blog = Blog(title=title, body=body, owner_id = owner_id)
            db.session.add(blog)
            db.session.commit()
            blogurl = "/blogpost?id="+ str(blog.id) 
            return redirect(blogurl)
        else:
            return render_template('new.html')
          
@app.route('/blogpost', methods=['GET'])
def trouble_one():
    
    blogid = request.args.get('id')
    abc = Blog.query.filter_by(id = blogid).first()
    return render_template('entry.html', abc=abc)

@app.route('/userpost', methods=['GET'])
def trouble_two():
    
    uid = request.args.get('user')
    user_id = Person.query.filter_by(name=uid ).first().id
    abc = Blog.query.filter_by(owner_id=user_id).all()
    return render_template('userblog.html', abc=abc)


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'
if __name__ == '__main__':
    app.run()