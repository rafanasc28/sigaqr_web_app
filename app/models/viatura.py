from datetime import datetime
from app import db
from uuid import uuid4

class MovimentoViatura(db.Model):
    __tablename__ = 'movimento_viatura'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    data_movimento = db.Column(db.Date, nullable=False, default=datetime.utcnow) # Data da ocorrência
    unidade = db.Column(db.String(100), nullable=False) # Ex: Galpão Principal, Filial X
    ordem_servico = db.Column(db.String(50)) # Ordem de serviço ou referência

    hora_entrada = db.Column(db.Time, nullable=False)
    hora_saida = db.Column(db.Time, nullable=True)

    veiculo_tipo = db.Column(db.String(50), nullable=False) # Caminhão, Van, Utilitário
    placa_veiculo = db.Column(db.String(10), nullable=False)
    condutor_nome = db.Column(db.String(100), nullable=False)

    tipo_movimentacao = db.Column(db.String(50), nullable=False) # Carga, Descarga, Devolução, Coleta, Outro
    detalhe_movimentacao = db.Column(db.String(255)) # Para "Outro" ou detalhes adicionais

    responsavel_atendimento = db.Column(db.String(100), nullable=False) # Funcionário que registrou/acompanhou

    data_registro_sistema = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_atualizacao = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'data_movimento': self.data_movimento.strftime('%d/%m/%Y') if self.data_movimento else None,
            'unidade': self.unidade,
            'ordem_servico': self.ordem_servico,
            'hora_entrada': self.hora_entrada.strftime('%H:%M') if self.hora_entrada else None,
            'hora_saida': self.hora_saida.strftime('%H:%M') if self.hora_saida else None,
            'veiculo_tipo': self.veiculo_tipo,
            'placa_veiculo': self.placa_veiculo,
            'condutor_nome': self.condutor_nome,
            'tipo_movimentacao': self.tipo_movimentacao,
            'detalhe_movimentacao': self.detalhe_movimentacao,
            'responsavel_atendimento': self.responsavel_atendimento,
            'data_registro_sistema': self.data_registro_sistema.strftime('%d/%m/%Y %H:%M') if self.data_registro_sistema else None,
        }

    def __repr__(self):
        return f"<MovimentoViatura {self.placa_veiculo} - {self.data_movimento.strftime('%d/%m/%Y')}>"