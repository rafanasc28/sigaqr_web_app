import os
from pathlib import Path
# from dotenv import load_dotenv # Mantenha se usa .env para desenvolvimento local

# Caminho do .env (um nível acima do diretório deste arquivo)
# env_path = Path(__file__).resolve().parent.parent / '.env'

# Carregar variáveis do .env se existir (mais útil para desenvolvimento local)
# if env_path.exists():
#     load_dotenv(env_path)
# else:
    # Esta mensagem pode aparecer nos logs do servidor se o .env não existir lá, o que é normal.
    # print(f"⚠️  Arquivo .env não encontrado em {env_path}")

class Config:
    # Chave Secreta - Deve ser definida pela variável de ambiente em produção
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Rafa115295Lou@_fallback_local_dev' # Adicionei um fallback mais claro

    # Configuração do Banco de Dados
    # 1. Tenta usar SQLALCHEMY_DATABASE_URI do ambiente (definido no WSGI)
    # 2. Se não encontrar, tenta usar DATABASE_URL do ambiente (para compatibilidade com outras plataformas)
    # 3. Se não encontrar nenhum, usa um SQLite local como fallback (para desenvolvimento)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
                              os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'sigaqr_local_dev.db')

    # Correção para URLs do PostgreSQL (se aplicável e se DATABASE_URL for usada)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Outras configurações
    # DEBUG deve ser False em produção (controlado pela variável de ambiente FLASK_ENV ou DEBUG)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

    # Chave Secreta
    SECRET_KEY = os.getenv('SECRET_KEY', 'Rafa115295Lou@')

    # Outras configurações que possam ser úteis no futuro
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
