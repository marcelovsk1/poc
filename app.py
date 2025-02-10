from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    # Endereço principal do usuário
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


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            session['admin'] = admin.email
            flash("Login realizado com sucesso!", "success")
            return redirect('/')
        else:
            flash("Credenciais inválidas. Tente novamente.", "danger")
    return render_template('login.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not email.endswith('@correios.com'):
            flash("O email deve conter '@correios.com'", "danger")
            return redirect('/register')
        hashed_password = generate_password_hash(password)
        new_admin = Admin(email=email, password=hashed_password)
        try:
            db.session.add(new_admin)
            db.session.commit()
            flash("Conta criada com sucesso! Faça login.", "success")
            return redirect('/login')
        except:
            flash("Erro ao criar conta. O email já está em uso.", "danger")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("Logout realizado com sucesso.", "success")
    return redirect('/login')

@app.route('/')
def index():
    if not session.get('admin'):
        flash("Por favor, faça login para acessar o sistema.", "danger")
        return redirect('/login')
    users = Users.query.all()
    return render_template('index.html', users=users)

# CREATE - adiciona o usuario e o endereco principal
@app.route('/new_user', methods=['POST'])
def create_users():
    new_user = request.form['name']
    new_email = request.form['email']
    new_password = request.form['password']
    street = request.form['street']
    number = request.form['number']
    complement = request.form['complement']
    zip_code = request.form['zip_code']
    city = request.form['city']
    state = request.form['state']
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

# CREATE - adiciona o endereco adicional
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
    if is_main:
        Addresses.query.filter_by(user_id=user.id, is_main=True).update({"is_main": False})
        user.street = street
        user.number = number
        user.complement = complement
        user.zip_code = zip_code
        user.city = city
        user.state = state

    new_address = Addresses(
        street=street, number=number, complement=complement,
        zip_code=zip_code, city=city, state=state, is_main=is_main, user_id=user.id
    )
    db.session.add(new_address)
    db.session.commit()
    return redirect('/')

# DELETE - usuario e os enderecos relacionados
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = Users.query.get(user_id)
    if user:
        Addresses.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
    return redirect('/')

# DELETE - endereco adicional
@app.route('/delete_address/<int:address_id>', methods=['POST'])
def delete_address(address_id):
    address = Addresses.query.get(address_id)
    db.session.delete(address)
    db.session.commit()
    return redirect('/')

# UPDATE - busca o usuario pelo id no banco de dados
@app.route('/edit_user/<int:user_id>', methods=['GET'])
def edit_user(user_id):
    user = Users.query.get(user_id)
    if user:
        return render_template('edit_user.html', user=user)
    else:
        return "Usuário não encontrado", 404
    
# UPDATE - seta o endereco como principal
@app.route('/set_primary_address/<int:address_id>', methods=['POST'])
def set_main_address(address_id):
    address = Addresses.query.get(address_id)
    if address:
        user = address.user
        old_main_address = Addresses.query.filter_by(user_id=user.id, is_main=True).first()
        if old_main_address:
            old_main_address.is_main = False
            user.street = address.street
            user.number = address.number
            user.complement = address.complement
            user.zip_code = address.zip_code
            user.city = address.city
            user.state = address.state
        address.is_main = True
        db.session.commit()
        return redirect('/')
    return "Endereço não encontrado", 404

# UPDATE - usuario
@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    user = Users.query.get(user_id)
    if user:
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

# UPDATE - endereco adicional
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

# CRUD - busca o CEP na API ViaCEP
@app.route('/buscar_cep', methods=['GET'])
def buscar_cep():
    cep = request.args.get('cep', '').strip()
    
    # Validação do CEP
    if not cep.isdigit() or len(cep) != 8:
        return {"erro": "CEP inválido. Certifique-se de que possui 8 dígitos."}, 400

    try:
        # Consulta à API ViaCEP
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        response.raise_for_status()  # Levanta exceções para erros de status HTTP
        data = response.json()

        # Verifica se o CEP foi encontrado
        if 'erro' in data:
            return {"erro": "CEP não encontrado."}, 404

        # Retorna os dados de endereço formatados
        return {
            "logradouro": data.get('logradouro', ''),
            "complemento": data.get('complemento', ''),
            "cidade": data.get('localidade', ''),
            "estado": data.get('uf', ''),
        }
    except requests.exceptions.RequestException as e:
        # Lida com erros de conexão ou requisição
        return {"erro": f"Erro ao buscar o CEP: {str(e)}"}, 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=2525)
