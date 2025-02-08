from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelo de Usuários (Agora inclui endereço principal)
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    # 🔹 Endereço principal do usuário
    street = db.Column(db.String(120), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    complement = db.Column(db.String(120))
    zip_code = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)

    # 🔹 Relacionamento: Um usuário pode ter vários endereços extras
    addresses = db.relationship('Addresses', backref='user', lazy=True)

# Modelo de Endereços Adicionais
class Addresses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(120), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    complement = db.Column(db.String(120))
    zip_code = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# CRUD - READ (Listar usuários e endereços)
@app.route('/')
def index():
    users = Users.query.all()
    return render_template('index.html', users=users)

# CRUD - CREATE (Criar novo usuário com endereço principal)
@app.route('/new_user', methods=['POST'])
def create_users():
    new_user = request.form['name']
    new_email = request.form['email']
    new_password = request.form['password']

    # 🔹 Endereço principal do usuário
    street = request.form['street']
    number = request.form['number']
    complement = request.form['complement']
    zip_code = request.form['zip_code']
    city = request.form['city']
    state = request.form['state']
    
    # Criar usuário com endereço principal
    user = Users(
        name=new_user, email=new_email, password=new_password,
        street=street, number=number, complement=complement,
        zip_code=zip_code, city=city, state=state
    )
    db.session.add(user)
    db.session.commit()
    
    return redirect('/')

# CRUD - CREATE (Adicionar novo endereço para um usuário existente)
@app.route('/new_address', methods=['POST'])
def create_address():
    user_name = request.form['name']  # O usuário é identificado pelo nome
    user = Users.query.filter_by(name=user_name).first()
    
    if user:
        street = request.form['street']
        number = request.form['number']
        complement = request.form['complement']
        zip_code = request.form['zip_code']
        city = request.form['city']
        state = request.form['state']

        # Criar novo endereço para o usuário
        address = Addresses(
            street=street, number=number, complement=complement,
            zip_code=zip_code, city=city, state=state, user_id=user.id
        )
        db.session.add(address)
        db.session.commit()
    
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Criar ou atualizar as tabelas
    app.run(debug=True, port=2525)
