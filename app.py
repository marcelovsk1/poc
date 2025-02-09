from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    #  main principal do usuário
    street = db.Column(db.String(120), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    complement = db.Column(db.String(120))
    zip_code = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)

    # Um usuário pode ter vários endereços extras
    addresses = db.relationship('Addresses', backref='user', lazy=True)

class Addresses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(120), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    complement = db.Column(db.String(120))
    zip_code = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
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

    main_address = Addresses(
        street=street, number=number, complement=complement,
        zip_code=zip_code, city=city, state=state, is_main=True, user_id=user.id
    )
    db.session.add(main_address)
    db.session.commit()
    
    return redirect('/')

# CRUD - CREATE (Adicionar novo endereço para um usuário existente)
@app.route('/new_address', methods=['POST'])
def create_address():
    user_name = request.form['name']
    user = Users.query.filter_by(name=user_name).first()
    
    if not user:
        return "Usuário não encontrado", 404

    street = request.form['street']
    number = request.form['number']
    complement = request.form['complement']
    zip_code = request.form['zip_code']
    city = request.form['city']
    state = request.form['state']
    is_main = request.form.get('is_main') == 'on'  

    # move o antigo endereço principal para "Endereços Adicionais"
    if is_main:
        Addresses.query.filter_by(user_id=user.id, is_main=True).update({"is_main": False})
        
        # atualiza os dados do usuário com o novo endereço principal
        user.street = street
        user.number = number
        user.complement = complement
        user.zip_code = zip_code
        user.city = city
        user.state = state

    # cria o novo endereço
    new_address = Addresses(
        street=street, number=number, complement=complement,
        zip_code=zip_code, city=city, state=state, 
        is_main=is_main, user_id=user.id
    )
    
    db.session.add(new_address)
    db.session.commit()
    
    return redirect('/')


# CRUD - DELETE (Remover usuário e endereços)
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = Users.query.get(user_id)
    
    if user:
        # deleta todos os endereços vinculados ao usuário primeiro
        Addresses.query.filter_by(user_id=user.id).delete()

        # deleta o usuário
        db.session.delete(user)
        db.session.commit()
    
    return redirect('/')


@app.route('/delete_address/<int:address_id>', methods=['POST'])
def delete_address(address_id):
    address = Addresses.query.get(address_id)
    db.session.delete(address)
    db.session.commit()
    return redirect('/')

# CRUD - UPDATE (Atualizar usuário e endereços)
# Users
@app.route('/edit_user/<int:user_id>', methods=['GET'])
def edit_user(user_id):
    user = Users.query.get(user_id)
    if user:
        return render_template('edit_user.html', user=user)
    else:
        return "Usuário não encontrado", 404

@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    user = Users.query.get(user_id)
    if user:
        # Atualiza os campos somente se forem enviados no formulário
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        user.password = request.form.get('password', user.password)
        user.street = request.form.get('street', user.street)
        user.number = request.form.get('number', user.number)
        user.complement = request.form.get('complement', user.complement)
        user.zip_code = request.form.get('zip_code', user.zip_code)
        user.city = request.form.get('city', user.city)
        user.state = request.form.get('state', user.state)

        db.session.commit()
        return redirect('/')
    else:
        return "Usuário não encontrado", 404

# Addresses
@app.route('/edit_address/<int:address_id>', methods=['GET'])
def edit_address(address_id):
    address = Addresses.query.get(address_id)
    if address:
        return render_template('edit_address.html', address=address)
    else:
        return "Endereço não encontrado", 404
    
@app.route('/update_address/<int:address_id>', methods=['POST'])
def update_address(address_id):
    address = Addresses.query.get(address_id)
    if address:
        address.street = request.form.get('street', address.street)
        address.number = request.form.get('number', address.number)
        address.complement = request.form.get('complement', address.complement)
        address.zip_code = request.form.get('zip_code', address.zip_code)
        address.city = request.form.get('city', address.city)
        address.state = request.form.get('state', address.state)

        db.session.commit()
        return redirect('/')
    else:
        return "Endereço não encontrado", 404
    

# CRUD - UPDATE (Definir endereço principal)
@app.route('/set_primary_address/<int:address_id>', methods=['POST'])
def set_main_address(address_id):
    address = Addresses.query.get(address_id)
    if address:
        # Buscar o usuário relacionado
        user = address.user
        
        # Mover o antigo endereço principal para "Endereços Adicionais"
        old_main_address = Addresses.query.filter_by(user_id=user.id, is_main=True).first()
        if old_main_address:
            old_main_address.is_main = False

            # Atualizar os campos do modelo `Users` para refletir o novo endereço principal
            user.street = address.street
            user.number = address.number
            user.complement = address.complement
            user.zip_code = address.zip_code
            user.city = address.city
            user.state = address.state

        # Marcar o novo endereço como principal
        address.is_main = True

        db.session.commit()
        return redirect('/')
    return "Endereço não encontrado", 404
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True, port=2525)
