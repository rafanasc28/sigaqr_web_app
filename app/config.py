import os
from pathlib import Path
from dotenv import load_dotenv

# Caminho do .env (um nível acima do diretório deste arquivo)
env_path = Path(__file__).resolve().parent.parent / '.env'

# Carregar variáveis do .env se existir
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"⚠️  Arquivo .env não encontrado em {env_path}")

class Config:
    # Configuração do Banco de Dados
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')

    # Correção automática para PostgreSQL se necessário
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Chave Secreta
    SECRET_KEY = os.getenv('SECRET_KEY', 'Rafa115295Lou@')

    # Outras configurações que possam ser úteis no futuro
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
