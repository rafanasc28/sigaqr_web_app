from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicializando o banco de dados
db = SQLAlchemy()
# Inicializando o Flask-Migrate
migrate = Migrate()

def create_app():
    # Criar a instância da aplicação Flask
    app = Flask(__name__)
    # Carregar as configurações do arquivo de configurações
    app.config.from_object('app.config.Config')

    # Inicializar o banco de dados e o Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Importando e configurando as rotas
    from .routes.main_routes import configure_routes
    configure_routes(app)

    # Importando e registrando o Blueprint de Viaturas
    from .routes.viatura_routes import viatura_bp
    app.register_blueprint(viatura_bp)

    # Importar modelos para o migrate reconhecer
    from .models import asset, viatura  # Adicionar viatura aqui

    # Retornar a aplicação Flask configurada
    return app
