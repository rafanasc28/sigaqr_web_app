import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Float, Text, Date, Time # Adicione os tipos que você usa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- CONFIGURAÇÕES ---
# String de conexão para o banco de dados SQLite ANTIGO
# Certifique-se que o arquivo do banco SQLite está acessível
OLD_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sigaqr_local_dev.db') # Ou o nome do seu arquivo .db
OLD_DB_URI = f'sqlite:///{OLD_DB_PATH}'

# String de conexão para o banco de dados MySQL NOVO no PythonAnywhere
# SUBSTITUA COM SUAS CREDENCIAIS REAIS
NEW_DB_HOST = 'sigaforalmox.mysql.pythonanywhere-services.com'
NEW_DB_USER = 'sigaforalmox'
NEW_DB_PASSWORD = 'SUA_SENHA_MYSQL_AQUI' # << MUITO IMPORTANTE: Substitua pela sua senha real
NEW_DB_NAME = 'sigaforalmox$default' # Ou o nome do seu banco de dados MySQL
NEW_DB_URI = f'mysql+pymysql://{NEW_DB_USER}:{NEW_DB_PASSWORD}@{NEW_DB_HOST}/{NEW_DB_NAME}'

# --- INICIALIZAÇÃO DOS BANCOS ---
old_engine = create_engine(OLD_DB_URI)
new_engine = create_engine(NEW_DB_URI)

OldSession = sessionmaker(bind=old_engine)
NewSession = sessionmaker(bind=new_engine)

old_session = OldSession()
new_session = NewSession()

Base = declarative_base() # Base para definir modelos se necessário, ou usar MetaData para refletir

# --- DEFINIÇÃO DOS MODELOS (deve espelhar seus modelos Flask-SQLAlchemy) ---
# Você PRECISA definir estruturas de tabela aqui que correspondam exatamente
# às suas tabelas 'asset' e 'movimento_viatura' (e outras que queira migrar).
# Seus modelos Flask-SQLAlchemy já definem isso, mas para um script autônomo
# pode ser mais fácil redefini-los aqui ou usar Table reflection.

# Exemplo para Asset (adapte EXATAMENTE aos seus campos e tipos)
class AssetOld(Base):
    __tablename__ = 'asset'
    # Mapeie todos os campos da sua tabela 'asset' no SQLite
    id = Column(String(36), primary_key=True)
    tipo = Column(String(20), nullable=False)
    descricao = Column(String(255), nullable=False)
    localizacao = Column(String(100))
    centro_custos = Column(String(50))
    afo = Column(String(20))
    empenho = Column(String(20))
    processo_licitatorio = Column(String(30))
    danfe = Column(String(44))
    data_entrada = Column(DateTime)
    data_danfe = Column(DateTime)
    codigo_despesa = Column(String(10))
    valor_bem = Column(Float)
    fornecedor = Column(String(100))
    numero_patrimonio = Column(String(50))
    numero_serial = Column(String(50))
    marca = Column(String(50))
    origem = Column(String(100))
    destino = Column(String(100))
    responsavel = Column(String(100))
    matricula_responsavel = Column(String(20))
    ultima_atualizacao = Column(DateTime) # Adicionado
    qr_code = Column(Text)

    def __repr__(self):
        return f"<AssetOld(id='{self.id}', descricao='{self.descricao}')>"

class MovimentoViaturaOld(Base):
    __tablename__ = 'movimento_viatura'
    # Mapeie todos os campos da sua tabela 'movimento_viatura' no SQLite
    id = Column(String(36), primary_key=True)
    data_movimento = Column(Date, nullable=False)
    unidade = Column(String(100), nullable=False) # Este é o "Setor Solicitante"
    ordem_servico = Column(String(50)) # Este é o "Número Identificador da Unidade"
    hora_entrada = Column(Time, nullable=False)
    hora_saida = Column(Time)
    veiculo_tipo = Column(String(50), nullable=False)
    placa_veiculo = Column(String(10), nullable=False)
    condutor_nome = Column(String(100), nullable=False)
    tipo_movimentacao = Column(String(50), nullable=False)
    detalhe_movimentacao = Column(String(255))
    responsavel_atendimento = Column(String(100), nullable=False)
    data_registro_sistema = Column(DateTime)
    ultima_atualizacao = Column(DateTime) # Adicionado

    def __repr__(self):
        return f"<MovimentoViaturaOld(id='{self.id}', placa_veiculo='{self.placa_veiculo}')>"

# --- FUNÇÃO DE MIGRAÇÃO ---
def migrate_table(OldModel, NewModelClassForReflection, new_session, new_engine):
    print(f"Migrando dados para a tabela {OldModel.__tablename__}...")
    all_old_data = old_session.query(OldModel).all()

    # Para inserir no novo banco, precisamos da estrutura da nova tabela.
    # Vamos refletir a tabela do novo banco de dados.
    meta = MetaData()
    # A tabela no novo banco de dados JÁ DEVE EXISTIR (criada pelo flask db upgrade)
    new_table_reflected = Table(OldModel.__tablename__, meta, autoload_with=new_engine)

    count = 0
    for old_row_obj in all_old_data:
        # Constrói um dicionário com os dados da linha antiga
        data_to_insert = {}
        for column in OldModel.__table__.columns:
            data_to_insert[column.name] = getattr(old_row_obj, column.name)

        try:
            # Insere os dados na tabela refletida
            stmt = new_table_reflected.insert().values(**data_to_insert)
            new_session.execute(stmt)
            count += 1
        except Exception as e:
            print(f"Erro ao inserir linha {data_to_insert.get('id', 'ID_DESCONHECIDO')} na tabela {OldModel.__tablename__}: {e}")
            # Você pode querer fazer um rollback parcial ou registrar o erro

    new_session.commit()
    print(f"Concluído! {count} linhas migradas para {OldModel.__tablename__}.")

if __name__ == '__main__':
    # Certifique-se que as tabelas no NOVO banco de dados (MySQL) JÁ EXISTEM!
    # Execute 'flask db upgrade' no PythonAnywhere ANTES de rodar este script.

    # Migrar Assets
    # Verifique se o nome da classe AssetOld corresponde à definição no seu SQLite
    migrate_table(AssetOld, AssetOld, new_session, new_engine)

    # Migrar MovimentoViatura
    # Verifique se o nome da classe MovimentoViaturaOld corresponde à definição no seu SQLite
    migrate_table(MovimentoViaturaOld, MovimentoViaturaOld, new_session, new_engine)

    # Adicione chamadas para outras tabelas que você precisa migrar

    old_session.close()
    new_session.close()
    print("Migração de dados concluída.")