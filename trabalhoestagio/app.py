from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from flask_caching import Cache
import users  # Importando a biblioteca de usuários

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do Cache
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)

audit_logs = []


@app.route('/')
@cache.cached(timeout=60)  # Cache da home page por 60 segundos
def home():
    if 'username' in session:
        user = session['username']
        return render_template('home.html', name=user, audit_logs=audit_logs)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificando o login usando a função da biblioteca users
        if users.validate_user(username, password):
            session['username'] = username
            # Adicionando log de auditoria
            audit_logs.append({
                'user': username,
                'event': 'Login',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            cache.delete('home')  # Invalida o cache da home quando o login ocorre
            return redirect(url_for('home'))
        else:
            error = 'Usuário ou senha inválidos'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    if 'username' in session:
        # Adicionando log de auditoria
        audit_logs.append({
            'user': session['username'],
            'event': 'Logout',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        session.pop('username', None)
        flash('Você saiu com sucesso!')
        cache.delete('home')  # Invalida o cache da home quando o logout ocorre
    return redirect(url_for('login'))


@app.route('/audit')
@cache.cached(timeout=60)  # Cache da página de auditoria por 60 segundos
def audit():
    if 'username' in session:
        return render_template('audit.html', audit_logs=audit_logs)
    flash('Você precisa estar logado para acessar a auditoria!')
    return redirect(url_for('login'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session:  # Apenas usuários logados podem adicionar novos
        flash('Você precisa estar logado para adicionar usuários!')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Adiciona um novo usuário através da biblioteca users
        if users.add_user(username, password):
            flash(f'Usuário {username} adicionado com sucesso!')
        else:
            flash(f'Erro: Usuário {username} já existe!')
        return redirect(url_for('home'))

    return render_template('add_user.html')


if __name__ == '__main__':
    app.run(debug=True)
