from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.viatura import MovimentoViatura
from datetime import datetime, time  # Adicionado time

# Criar um Blueprint para o módulo de viaturas
viatura_bp = Blueprint('viaturas', __name__, url_prefix='/viaturas')


@viatura_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_movimento():
    if request.method == 'POST':
        try:
            # Coleta de dados do formulário
            data_movimento_str = request.form.get('data_movimento')
            hora_entrada_str = request.form.get('hora_entrada')
            hora_saida_str = request.form.get('hora_saida')

            novo_movimento = MovimentoViatura(
                data_movimento=datetime.strptime(data_movimento_str,
                                                 '%Y-%m-%d').date() if data_movimento_str else datetime.utcnow().date(),
                unidade=request.form.get('unidade'),
                ordem_servico=request.form.get('ordem_servico'),
                hora_entrada=datetime.strptime(hora_entrada_str, '%H:%M').time() if hora_entrada_str else None,
                # hora_saida será preenchida na edição/saída
                veiculo_tipo=request.form.get('veiculo_tipo'),
                placa_veiculo=request.form.get('placa_veiculo').upper(),
                condutor_nome=request.form.get('condutor_nome'),
                tipo_movimentacao=request.form.get('tipo_movimentacao'),
                detalhe_movimentacao=request.form.get('detalhe_movimentacao'),
                responsavel_atendimento=request.form.get('responsavel_atendimento')
                # Idealmente pegar do usuário logado, se aplicável
            )
            db.session.add(novo_movimento)
            db.session.commit()
            flash('Movimento de viatura registrado com sucesso!', 'success')
            return redirect(url_for('viaturas.listar_movimentos'))
        except ValueError as e:
            db.session.rollback()
            flash(f'Erro de formato nos dados: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro inesperado ao registrar movimento: {str(e)}', 'danger')
            # Adicionar log aqui: app.logger.error(f"Erro ao registrar movimento: {str(e)}")

    # Valores padrão para o formulário GET
    default_data = datetime.utcnow().strftime('%Y-%m-%d')
    default_hora_entrada = datetime.now().strftime('%H:%M')

    return render_template('viaturas/registrar_movimento.html',
                           modo_edicao=False,
                           default_data=default_data,
                           default_hora_entrada=default_hora_entrada)


@viatura_bp.route('/')
@viatura_bp.route('/listar')
def listar_movimentos():
    query = MovimentoViatura.query

    # Coletar parâmetros de filtro da URL
    unidade_filtro = request.args.get('unidade')
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')
    hora_inicial_str = request.args.get('hora_inicial')
    hora_final_str = request.args.get('hora_final')
    placa_filtro = request.args.get('placa')
    tipo_mov_filtro = request.args.get('tipo_movimentacao')
    condutor_filtro = request.args.get('condutor')
    responsavel_filtro = request.args.get('responsavel')

    # Aplicar filtros à query
    if unidade_filtro:
        query = query.filter(MovimentoViatura.unidade.ilike(f'%{unidade_filtro}%'))
    if placa_filtro:
        query = query.filter(MovimentoViatura.placa_veiculo.ilike(f'%{placa_filtro}%'))
    if tipo_mov_filtro:
        query = query.filter(MovimentoViatura.tipo_movimentacao == tipo_mov_filtro)
    if condutor_filtro:
        query = query.filter(MovimentoViatura.condutor_nome.ilike(f'%{condutor_filtro}%'))
    if responsavel_filtro:
        query = query.filter(MovimentoViatura.responsavel_atendimento.ilike(f'%{responsavel_filtro}%'))

    if data_inicial_str:
        try:
            data_inicial_obj = datetime.strptime(data_inicial_str, '%Y-%m-%d').date()
            query = query.filter(MovimentoViatura.data_movimento >= data_inicial_obj)
        except ValueError:
            flash('Formato de Data Inicial inválido. Use AAAA-MM-DD.', 'warning')

    if data_final_str:
        try:
            data_final_obj = datetime.strptime(data_final_str, '%Y-%m-%d').date()
            query = query.filter(MovimentoViatura.data_movimento <= data_final_obj)
        except ValueError:
            flash('Formato de Data Final inválido. Use AAAA-MM-DD.', 'warning')

    if hora_inicial_str:
        try:
            hora_inicial_obj = datetime.strptime(hora_inicial_str, '%H:%M').time()
            # Para filtrar por hora_entrada, pode ser necessário considerar a data também,
            # ou se o campo for apenas Time, aplicar diretamente.
            # Se data_inicial_str for obrigatório com hora_inicial_str, a query pode ser mais precisa.
            query = query.filter(MovimentoViatura.hora_entrada >= hora_inicial_obj)
        except ValueError:
            flash('Formato de Hora Inicial inválido. Use HH:MM.', 'warning')

    if hora_final_str:
        try:
            hora_final_obj = datetime.strptime(hora_final_str, '%H:%M').time()
            query = query.filter(MovimentoViatura.hora_entrada <= hora_final_obj)
        except ValueError:
            flash('Formato de Hora Final inválido. Use HH:MM.', 'warning')

    movimentos = query.order_by(MovimentoViatura.data_movimento.desc(), MovimentoViatura.hora_entrada.desc()).all()

    # Passar datetime para o template para o modal de registrar saída
    # Também é bom passar os argumentos do request para repopular os filtros,
    # embora o HTML já esteja fazendo isso com request.args.get
    return render_template(
        'viaturas/listar_movimentos.html',
        movimentos=movimentos,
        datetime=datetime,  # Para o modal de registrar saída
        request_args=request.args  # Para facilitar acesso no template se necessário
    )

@viatura_bp.route('/editar/<movimento_id>', methods=['GET', 'POST'])
def editar_movimento(movimento_id):
    movimento = MovimentoViatura.query.get_or_404(movimento_id)
    if request.method == 'POST':
        try:
            data_movimento_str = request.form.get('data_movimento')
            hora_entrada_str = request.form.get('hora_entrada')
            hora_saida_str = request.form.get('hora_saida')

            movimento.data_movimento = datetime.strptime(data_movimento_str,
                                                         '%Y-%m-%d').date() if data_movimento_str else movimento.data_movimento
            movimento.unidade = request.form.get('unidade', movimento.unidade)
            movimento.ordem_servico = request.form.get('ordem_servico', movimento.ordem_servico)
            movimento.hora_entrada = datetime.strptime(hora_entrada_str,
                                                       '%H:%M').time() if hora_entrada_str else movimento.hora_entrada

            if hora_saida_str:  # Apenas atualiza se fornecido
                movimento.hora_saida = datetime.strptime(hora_saida_str, '%H:%M').time()

            movimento.veiculo_tipo = request.form.get('veiculo_tipo', movimento.veiculo_tipo)
            movimento.placa_veiculo = request.form.get('placa_veiculo', movimento.placa_veiculo).upper()
            movimento.condutor_nome = request.form.get('condutor_nome', movimento.condutor_nome)
            movimento.tipo_movimentacao = request.form.get('tipo_movimentacao', movimento.tipo_movimentacao)
            movimento.detalhe_movimentacao = request.form.get('detalhe_movimentacao', movimento.detalhe_movimentacao)
            movimento.responsavel_atendimento = request.form.get('responsavel_atendimento',
                                                                 movimento.responsavel_atendimento)

            db.session.commit()
            flash('Movimento atualizado com sucesso!', 'success')
            return redirect(url_for('viaturas.listar_movimentos'))
        except ValueError as e:
            db.session.rollback()
            flash(f'Erro de formato nos dados: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro inesperado ao atualizar movimento: {str(e)}', 'danger')
            # Adicionar log aqui: app.logger.error(f"Erro ao editar movimento {movimento_id}: {str(e)}")

    # Formatar datas e horas para exibição no formulário
    data_movimento_form = movimento.data_movimento.strftime('%Y-%m-%d') if movimento.data_movimento else ''
    hora_entrada_form = movimento.hora_entrada.strftime('%H:%M') if movimento.hora_entrada else ''
    hora_saida_form = movimento.hora_saida.strftime('%H:%M') if movimento.hora_saida else ''

    return render_template('viaturas/registrar_movimento.html',
                           modo_edicao=True,
                           movimento=movimento,
                           data_movimento_form=data_movimento_form,
                           hora_entrada_form=hora_entrada_form,
                           hora_saida_form=hora_saida_form)


# Você pode adicionar uma rota específica para registrar apenas a saída se preferir
@viatura_bp.route('/registrar_saida/<movimento_id>', methods=['POST'])
def registrar_saida(movimento_id):
    movimento = MovimentoViatura.query.get_or_404(movimento_id)
    try:
        hora_saida_str = request.form.get('hora_saida_modal')  # Supondo que virá de um campo de um modal
        if not hora_saida_str:
            flash('Hora de saída é obrigatória.', 'warning')
            return redirect(url_for('viaturas.listar_movimentos'))

        movimento.hora_saida = datetime.strptime(hora_saida_str, '%H:%M').time()
        db.session.commit()
        flash(f'Saída registrada para a placa {movimento.placa_veiculo}.', 'success')
    except ValueError:
        db.session.rollback()
        flash('Formato de hora de saída inválido.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar saída: {str(e)}', 'danger')
    return redirect(url_for('viaturas.listar_movimentos'))