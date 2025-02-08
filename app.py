from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Addresses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    # 🔹 Relacionamento: Um usuário pode ter vários endereços
    addresses = db.relationship('Addresses', backref='user', lazy=True)

# CRUD - READ (Exibir usuários e endereços)
@app.route('/')
def index():
    users = Users.query.all()
    return render_template('index.html', users=users)

# CRUD - CREATE (Criar novo usuário e endereço inicial)
@app.route('/new_user', methods=['POST'])
def create_users():
    new_user = request.form['name']
    new_email = request.form['email']
    new_password = request.form['password']
    new_address = request.form['address']
    
    user = Users(name=new_user, email=new_email, password=new_password)
    db.session.add(user)
    db.session.commit()

    # Criar endereço inicial associado ao usuário
    address = Addresses(address=new_address, user_id=user.id)
    db.session.add(address)
    db.session.commit()
    
    return redirect('/')

# CRUD - CREATE (Adicionar novo endereço para um usuário existente)
@app.route('/new_address', methods=['POST'])
def create_address():
    new_address = request.form['address']
    user_name = request.form['name']  

    user = Users.query.filter_by(name=user_name).first()
    
    if user:
        address = Addresses(address=new_address, user_id=user.id)
        db.session.add(address)
        db.session.commit()
    
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Criar ou atualizar as tabelas
    app.run(debug=True, port=2525)
