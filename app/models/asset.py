from datetime import datetime
import io
import base64
import qrcode
from app import db
from uuid import uuid4


class Asset(db.Model):
    """
    Modelo de Bem Patrimonial - Versão com nomes originais
    """

    __tablename__ = 'asset'

    # Campos básicos
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    tipo = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)

    # Campos para item novo
    localizacao = db.Column(db.String(100))
    centro_custos = db.Column(db.String(50))
    afo = db.Column(db.String(20))
    empenho = db.Column(db.String(20))
    processo_licitatorio = db.Column(db.String(30))
    danfe = db.Column(db.String(44))
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    data_danfe = db.Column(db.DateTime)
    codigo_despesa = db.Column(db.String(10))
    valor_bem = db.Column(db.Float, default=0)
    fornecedor = db.Column(db.String(100))

    # Campos para item remanejado
    numero_patrimonio = db.Column(db.String(50))
    numero_serial = db.Column(db.String(50))
    marca = db.Column(db.String(50))
    origem = db.Column(db.String(100))
    destino = db.Column(db.String(100))

    # Responsável
    responsavel = db.Column(db.String(100), default='')
    matricula_responsavel = db.Column(db.String(20), default='')

    ultima_atualizacao = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # QR Code
    qr_code = db.Column(db.Text)

    def to_dict(self, for_qrcode=False):
        """Retorna os dados do bem em formato de dicionário"""
        base_url = "https://turtle-settling-mule.ngrok-free.app"

        if for_qrcode:
            # Versão simplificada apenas para o QR Code
            return f"{base_url}/detalhes/{self.id}"
        else:
            # Versão completa para outros usos
            dados = {
                'id': self.id,
                'tipo': self.tipo.upper(),
                'descricao': self.descricao,
                'responsavel': self.responsavel,
                'matricula_responsavel': self.matricula_responsavel,
                'data_entrada': self.data_entrada.strftime('%d/%m/%Y') if self.data_entrada else None,
                'url_detalhes': f"{base_url}/detalhes/{self.id}"
            }

            if self.tipo == 'novo':
                dados.update({
                    'localizacao': self.localizacao,
                    'centro_custos': self.centro_custos,
                    'afo': self.afo,
                    'valor': f"R$ {self.valor_bem:,.2f}" if self.valor_bem else None,
                    'fornecedor': self.fornecedor
                })
            else:
                dados.update({
                    'numero_patrimonio': self.numero_patrimonio,
                    'numero_serial': self.numero_serial,
                    'marca': self.marca,
                    'origem': self.origem,
                    'destino': self.destino
                })

            return dados

    def generate_qr_code(self):
        """Gera o QR Code apenas com a URL de detalhes"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        # Codifica APENAS a URL, sem os dados extras
        base_url = "https://turtle-settling-mule.ngrok-free.app"
        qr.add_data(f"{base_url}/detalhes/{self.id}")

        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        self.qr_code = base64.b64encode(buffered.getvalue()).decode()

    def get_qr_code_image(self):
        """Retorna a imagem do QR Code pronto para uso em HTML"""
        if not self.qr_code:
            self.generate_qr_code()
        return f"data:image/png;base64,{self.qr_code}"

    def __repr__(self):
        return f"<Asset {self.id} - {self.descricao[:20]}...>"