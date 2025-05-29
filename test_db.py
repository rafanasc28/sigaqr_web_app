from app import create_app, db

app = create_app()

with app.app_context():
    try:
        db.engine.connect()
        print("✅ Conexão com SQLite bem-sucedida!")
        print(f"Database criado em: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")