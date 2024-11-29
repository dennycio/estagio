# users.py

users_db = {
    'newuser': 'newpassword',  # Exemplo de um usuário pré-existente
    'admin': '1234',       # Usuário de teste administrador
    'testuser': 'test123',     # Usuário de teste comum
    'guest': 'guestpassword'   # Usuário de teste com acesso limitado
}

def add_user(username, password):
    """ Adiciona um novo usuário ao sistema """
    if username in users_db:
        return False  # Usuário já existe
    users_db[username] = password
    return True

def validate_user(username, password):
    """ Valida o usuário e senha """
    return users_db.get(username) == password

def get_users():
    """ Retorna todos os usuários (útil para auditoria ou administração) """
    return users_db
