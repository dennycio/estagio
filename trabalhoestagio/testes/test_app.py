import pytest
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from datetime import datetime

# Função de configuração do app
def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'  # Chave secreta para a sessão

    # Configurar o LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Função para carregar os usuários a partir do arquivo JSON
    def load_users():
        try:
            with open('users.json', 'r') as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}
        return users

    # Função para salvar os usuários no arquivo JSON
    def save_users(users):
        with open('users.json', 'w') as f:
            json.dump(users, f)

    # Função para carregar os eventos de auditoria
    def load_audit_logs():
        try:
            with open('auditoria.json', 'r') as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        return logs

    # Função para registrar um evento de auditoria
    def log_audit_event(event_type, username):
        logs = load_audit_logs()
        event = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event_type,
            "user": username
        }
        logs.append(event)
        with open('auditoria.json', 'w') as f:
            json.dump(logs, f)

    # Classe para o usuário (usada pelo Flask-Login)
    class User(UserMixin):
        def __init__(self, id):
            self.id = id

    # Carregar o usuário baseado no ID
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            audit_logs = load_audit_logs()
            return render_template('home.html', name=current_user.id, audit_logs=audit_logs)
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))  # Se o usuário já estiver logado, redireciona para a página principal

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Carregar usuários do arquivo JSON
            users = load_users()

            # Verificar se o usuário e senha são válidos
            if username in users and users[username]['password'] == password:
                user = User(username)
                login_user(user)
                log_audit_event("Login", username)  # Registrar evento de login
                return redirect(url_for('home'))

            # Se o login falhar
            log_audit_event("Failed login attempt", username)  # Registrar tentativa de login falha
            return 'Credenciais inválidas. Tente novamente.'

        return render_template('login.html')

    @app.route('/audit')
    @login_required
    def audit():
        # Carregar os logs de auditoria
        audit_logs = load_audit_logs()
        return render_template('audit.html', audit_logs=audit_logs)

    @app.route('/logout')
    def logout():
        log_audit_event("Logout", current_user.id)  # Registrar evento de logout
        logout_user()
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Carregar os usuários
            users = load_users()

            if username in users:
                return 'Usuário já existe.'

            # Adicionar o novo usuário
            users[username] = {"password": password}
            save_users(users)
            log_audit_event("User registered", username)  # Registrar evento de registro
            return 'Usuário registrado com sucesso!'

        return render_template('register.html')

    return app


# Testes Unitários
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def test_user_registration(client):
    # Teste de registro de usuário
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword'
    })
    assert response.status_code == 200
    # Comparar com string, agora utilizando decode('utf-8')
    assert 'Usuário registrado com sucesso!' in response.data.decode('utf-8')


def test_login(client):
    # Teste de login
    response = client.post('/login', data={
        'username': 'newuser',
        'password': 'newpassword'
    })
    assert response.status_code == 200
    # Verificar se o login foi bem-sucedido (usuário redirecionado para home)
    assert 'Bem-vindo!' in response.data.decode('utf-8')


def test_failed_login(client):
    # Teste de login falho
    response = client.post('/login', data={
        'username': 'newuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200
    # Verificar mensagem de erro para credenciais inválidas
    assert 'Credenciais inválidas. Tente novamente.' in response.data.decode('utf-8')


def test_logout(client):
    # Teste de logout
    client.post('/login', data={
        'username': 'newuser',
        'password': 'newpassword'
    })
    response = client.get('/logout')
    assert response.status_code == 302  # Redirecionamento após logout
    assert 'Login com GitHub' in response.data.decode('utf-8')


def test_audit_log(client):
    # Teste de auditoria
    client.post('/login', data={
        'username': 'newuser',
        'password': 'newpassword'
    })
    response = client.get('/audit')
    assert response.status_code == 200
    # Verificar se logs de auditoria estão sendo exibidos
    assert 'Login' in response.data.decode('utf-8')
