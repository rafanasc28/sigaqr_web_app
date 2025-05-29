import base64
import re
import uuid
from datetime import datetime
from functools import wraps
from io import BytesIO
import qrcode
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.asset import Asset


def configure_routes(app):
    def sanitize_input(data):
        """Prevenção básica contra XSS/SQL Injection"""
        if re.search(r"[\"\';<>]", str(data)):
            abort(400, "Caracteres inválidos detectados")
        return str(data).strip()

    def required_role(role):
        """Decorator para controle de acesso"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated or current_user.cargo != role:
                    abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @app.route('/')
    @app.route('/home')
    def home():
        return render_template('home.html')

    @app.route('/cadastrar', methods=['GET', 'POST'])
    def generate_qr():
        global new_asset
        if request.method == 'POST':
            try:
                tipo = request.form['tipo']  # Agora pegando apenas 'tipo' que é comum a ambos

                # Tratamento diferente para cada tipo de item
                if tipo == 'novo':
                    data_entrada = datetime.strptime(request.form['data_entrada'], '%Y-%m-%d')
                    data_danfe_str = request.form.get('data_danfe')
                    data_danfe = datetime.strptime(data_danfe_str, '%Y-%m-%d') if data_danfe_str else None

                    new_asset = Asset(
                        id=str(uuid.uuid4()),
                        tipo=tipo,
                        descricao=request.form['descricao'],
                        localizacao=request.form['localizacao'],
                        centro_custos=request.form['centro_custos'],
                        afo=request.form['afo'],
                        empenho=request.form.get('empenho'),
                        processo_licitatorio=request.form.get('processo_licitatorio'),
                        danfe=request.form.get('danfe'),
                        data_entrada=data_entrada,
                        data_danfe=data_danfe,
                        codigo_despesa=request.form.get('codigo_despesa'),
                        valor_bem=float(request.form['valor_bem']),
                        responsavel=request.form['responsavel'],
                        matricula_responsavel=request.form['matricula_responsavel'],
                        fornecedor=request.form.get('fornecedor')
                    )

                elif tipo == 'remanejado':
                    new_asset = Asset(
                        id=str(uuid.uuid4()),
                        tipo=tipo,
                        descricao=request.form['descricao'],
                        numero_patrimonio=request.form.get('numero_patrimonio'),
                        numero_serial=request.form.get('numero_serial'),
                        marca=request.form.get('marca'),
                        origem=request.form.get('origem'),
                        destino=request.form.get('destino'),
                        responsavel=request.form['responsavel'],
                        matricula_responsavel=request.form['matricula_responsavel']
                    )

                db.session.add(new_asset)
                db.session.commit()

                # Gera QR Code com os dados específicos
                new_asset.generate_qr_code()
                db.session.commit()

                return redirect(url_for('detalhes', asset_id=new_asset.id))

            except ValueError as e:
                db.session.rollback()
                flash(f'Erro de formato: {str(e)}', 'danger')
                return redirect(url_for('generate_qr'))

            except Exception as e:
                db.session.rollback()
                flash(f'Erro inesperado: {str(e)}', 'danger')
                return redirect(url_for('generate_qr'))

        return render_template('generate.html', modo_edicao=False)  # Adicionando modo_edicao=True

    @app.route('/lista')
    def listar_bens():
        try:
            # Busca todos os itens ordenados por data de cadastro
            bens = Asset.query.order_by(Asset.data_entrada.desc()).all()

            # Verifica se há itens
            if not bens:
                flash('Nenhum bem cadastrado ainda.', 'info')

            return render_template('lista.html', bens=bens)

        except Exception as e:
            app.logger.error(f'Erro ao listar bens: {str(e)}')
            flash('Ocorreu um erro ao carregar a lista de bens.', 'danger')
            return redirect(url_for('home'))

    @app.route('/detalhes/<asset_id>')
    def detalhes(asset_id):
        asset = Asset.query.get_or_404(asset_id)

        # Gera QR Code para exibição na página
        qr = qrcode.QRCode(version=1, box_size=6, border=1)
        qr.add_data(f"https://turtle-settling-mule.ngrok-free.app/detalhes/{asset.id}")
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        template = 'detalhes_remanejado.html' if asset.tipo == 'remanejado' else 'detalhes.html'
        return render_template(template, asset=asset, qr_code=img_str)

    @app.route('/ler-qr')
    def scan_qr():
        return render_template('scan.html')

    # Rota para edição (reutiliza a generate.html)
    @app.route('/editar/<asset_id>', methods=['GET', 'POST'])
    def editar_asset(asset_id):
        asset = Asset.query.get_or_404(asset_id)

        if request.method == 'POST':
            try:
                # ===== CAMPOS COMUNS =====
                asset.descricao = request.form.get('descricao', asset.descricao)
                asset.responsavel = request.form.get('responsavel', asset.responsavel)
                asset.matricula_responsavel = request.form.get('matricula_responsavel', asset.matricula_responsavel)

                # ===== CAMPOS PARA ITENS NOVOS =====
                if asset.tipo == 'novo':
                    asset.localizacao = request.form.get('localizacao', asset.localizacao)
                    asset.centro_custos = request.form.get('centro_custos', asset.centro_custos)
                    asset.afo = request.form.get('afo', asset.afo)
                    asset.empenho = request.form.get('empenho', asset.empenho)
                    asset.processo_licitatorio = request.form.get('processo_licitatorio', asset.processo_licitatorio)
                    asset.danfe = request.form.get('danfe', asset.danfe)
                    asset.codigo_despesa = request.form.get('codigo_despesa', asset.codigo_despesa)
                    asset.valor_bem = float(request.form.get('valor_bem', asset.valor_bem or 0))
                    asset.fornecedor = request.form.get('fornecedor', asset.fornecedor)

                    # Tratamento de datas
                    if request.form.get('data_entrada'):
                        asset.data_entrada = datetime.strptime(request.form.get('data_entrada'), '%Y-%m-%d')
                    if request.form.get('data_danfe'):
                        asset.data_danfe = datetime.strptime(request.form.get('data_danfe'), '%Y-%m-%d')

                # ===== CAMPOS PARA ITENS REMANEJADOS =====
                elif asset.tipo == 'remanejado':
                    asset.numero_patrimonio = request.form.get('numero_patrimonio', asset.numero_patrimonio)
                    asset.numero_serial = request.form.get('numero_serial', asset.numero_serial)  # Note que no modelo é 'numero_serial' não 'numero_serie'
                    asset.marca = request.form.get('marca', asset.marca)
                    asset.origem = request.form.get('origem', asset.origem)
                    asset.destino = request.form.get('destino', asset.destino)

                db.session.commit()
                flash('Item atualizado com sucesso!', 'success')
                return redirect(url_for('detalhes', asset_id=asset.id))

            except ValueError as e:
                db.session.rollback()
                flash(f'Erro de formato nos dados: {str(e)}', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao atualizar item: {str(e)}', 'danger')
                app.logger.error(f"Erro na edição do asset {asset_id}: {str(e)}")

        return render_template('generate.html', modo_edicao=True, asset=asset)

        # Rota para exclusão
    @app.route('/excluir/<asset_id>', methods=['POST'])  # Adicione methods=['POST']
    def excluir_asset(asset_id):
        try:
            asset = Asset.query.get_or_404(asset_id)
            db.session.delete(asset)
            db.session.commit()
            flash('Item excluído com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Erro ao excluir item: {str(e)}')
            flash('Erro ao excluir item', 'danger')
        return redirect(url_for('listar_bens'))