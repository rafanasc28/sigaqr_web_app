import os
from pathlib import Path
# A importação do load_dotenv é mais relevante para desenvolvimento local.
# No PythonAnywhere, as variáveis de ambiente são definidas no arquivo WSGI.
# from dotenv import load_dotenv

# Lógica para carregar .env (útil para desenvolvimento local, opcional para produção no PA)
# Se você não usa um arquivo .env no desenvolvimento local, pode remover esta seção.
# env_path = Path(__file__).resolve().parent.parent / '.env'
# if env_path.exists():
#     load_dotenv(dotenv_path=env_path)
# else:
    # Esta mensagem aparecerá nos logs do servidor do PythonAnywhere se o .env não for encontrado lá,
    # o que é esperado, já que as variáveis de ambiente são definidas no arquivo WSGI.
    # print(f"⚠️  Arquivo .env não encontrado em {env_path} (Isso é normal no servidor se as variáveis de ambiente são definidas de outra forma)")

class Config:
    # Chave Secreta:
    # Em produção (PythonAnywhere), esta variável DEVE ser definida no seu arquivo WSGI.
    # O valor aqui é um fallback para desenvolvimento local se a variável de ambiente não estiver definida.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma_chave_secreta_local_muito_forte_e_diferente_da_de_producao'

    # Configuração do Banco de Dados:
    # 1. Tenta usar SQLALCHEMY_DATABASE_URI do ambiente (que você define no arquivo WSGI para o MySQL do PythonAnywhere).
    # 2. Se não encontrar, tenta usar DATABASE_URL do ambiente (para compatibilidade com outras plataformas ou preferências).
    # 3. Se não encontrar nenhum dos dois, usa um banco de dados SQLite local como fallback (útil para desenvolvimento local).
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
                              os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'sigaqr_local_dev.db')

    # Correção para URLs do PostgreSQL caso DATABASE_URL seja usada e seja para PostgreSQL.
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuração de Debug:
    # Em produção (PythonAnywhere), esta variável DEVE ser 'False'.
    # Você pode definir FLASK_ENV=production ou DEBUG=False no seu arquivo WSGI.
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

    # Outras configurações da sua aplicação podem vir aqui.
    # Exemplo:
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')