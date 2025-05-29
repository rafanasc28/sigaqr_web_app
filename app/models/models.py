from datetime import datetime

from app import db  # Certifique-se que 'db' está definido em app/__init__.py

class Asset(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    fornecedor = db.Column(db.String(100))  # Exemplo de campo
    # ... outros campos

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(50))  # 'EDIT' ou 'DELETE'
    asset_id = db.Column(db.String(36), db.ForeignKey('asset.id'))
    usuario = db.Column(db.String(50))  # Matrícula
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)