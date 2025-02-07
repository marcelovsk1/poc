from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)

    
# CRUD - READ
@app.route('/')
def index():
    users = Users.query.all()
    return render_template('index.html', users=users)


# CRUD - CREATE
def create_user():
    new_user = Users

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Recria as tabelas com base nos modelos atuais

    app.run(debug=True, port=2525)