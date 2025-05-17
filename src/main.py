import os
import sys
import uuid # Para gerar IDs únicos
import datetime # Para manipulação de datas
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, request, redirect, url_for, session, flash

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['SECRET_KEY'] = 'escola_secret_key_#$!321'

# --- DADOS MOCADOS (Simulação de Banco de Dados) ---
ADMINS_MOCK = {
    "admin": {"senha": "adminpass", "nome": "Administrador Principal"}
}

PROFESSORES_MOCK = {
    "prof001": {"username": "professor1", "senha": "senha123", "nome": "Professor Carlos", "disciplinas": ["Matemática", "Física"]},
    "prof002": {"username": "professor2", "senha": "securepass", "nome": "Professora Ana", "disciplinas": ["Português", "História"]}
}

ALUNOS_MOCK = {
    "6A": [
        {"id": "aluno1_id", "nome": "João Silva", "pai_username": "pai_joao"},
        {"id": "aluno2_id", "nome": "Maria Oliveira", "pai_username": "mae_maria"}
    ],
    "7B": [
        {"id": "aluno3_id", "nome": "Pedro Santos", "pai_username": "pai_pedro"},
        {"id": "aluno4_id", "nome": "Ana Costa", "pai_username": "mae_ana"}
    ]
}
TURMAS_MOCK = ["6A", "7B"]

PAIS_MOCK = {
    "pai_joao": {"senha": "paisilva", "nome": "Sr. Silva (Pai de João)", "filho_id": "aluno1_id"},
    "mae_maria": {"senha": "maemaria", "nome": "Sra. Oliveira (Mãe de Maria)", "filho_id": "aluno2_id"},
    "pai_pedro": {"senha": "paipedro123", "nome": "Sr. Santos (Pai de Pedro)", "filho_id": "aluno3_id"},
    "mae_ana": {"senha": "maeana123", "nome": "Sra. Costa (Mãe de Ana)", "filho_id": "aluno4_id"}
}

NOTAS_GLOBAIS = []

MENSALIDADES_MOCK = {
    "mensalidade1_id": {
        "id_mensalidade": "mensalidade1_id",
        "id_aluno": "aluno1_id",
        "mes_referencia": "2025-05",
        "valor": 500.00,
        "data_vencimento": "2025-05-10",
        "status": "Pendente", # Pendente, Pago, Vencido, Em Processamento
        "data_pagamento": None,
        "codigo_boleto_simulado": None,
        "link_boleto_simulado": None
    },
    "mensalidade2_id": {
        "id_mensalidade": "mensalidade2_id",
        "id_aluno": "aluno2_id",
        "mes_referencia": "2025-05",
        "valor": 550.00,
        "data_vencimento": "2025-05-10",
        "status": "Pago",
        "data_pagamento": "2025-05-08",
        "codigo_boleto_simulado": "simulado123456",
        "link_boleto_simulado": "/boleto/simulado123456.pdf"
    },
    "mensalidade3_id": {
        "id_mensalidade": "mensalidade3_id",
        "id_aluno": "aluno1_id",
        "mes_referencia": "2025-06",
        "valor": 500.00,
        "data_vencimento": "2025-06-10",
        "status": "Pendente",
        "data_pagamento": None,
        "codigo_boleto_simulado": None,
        "link_boleto_simulado": None
    }
}

# --- ROTAS DE ADMINISTRAÇÃO ---
@app.route('/login_admin', methods=['GET'])
def login_admin_get():
    return render_template('login_admin.html')

@app.route('/login_admin', methods=['POST'])
def login_admin_post():
    username = request.form.get('username')
    password = request.form.get('password')
    admin_user = ADMINS_MOCK.get(username)

    if admin_user and admin_user['senha'] == password:
        session['user_type'] = 'admin'
        session['admin_username'] = username
        session['nome_display_admin'] = admin_user['nome']
        flash('Login de administrador realizado com sucesso!', 'success')
        return redirect(url_for('dashboard_admin'))
    else:
        flash('Usuário ou senha de administrador inválidos.', 'danger')
        return redirect(url_for('login_admin_get'))

@app.route('/dashboard_admin')
def dashboard_admin():
    if session.get('user_type') == 'admin':
        return render_template('dashboard_admin.html')
    flash('Você precisa estar logado como administrador para acessar esta página.', 'info')
    return redirect(url_for('login_admin_get'))

# CRUD Professores
@app.route('/admin/professores')
def admin_gerenciar_professores():
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))
    return render_template('admin_professores.html', professores=PROFESSORES_MOCK)

@app.route('/admin/professores/add', methods=['POST'])
def admin_add_professor():
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))
    
    nome = request.form.get('nome')
    username = request.form.get('username')
    senha = request.form.get('senha')
    disciplinas_str = request.form.get('disciplinas', '')
    disciplinas = [d.strip() for d in disciplinas_str.split(',') if d.strip()] 

    if not nome or not username or not senha:
        flash('Nome, usuário e senha são obrigatórios.', 'danger')
        return redirect(url_for('admin_gerenciar_professores'))

    # Verifica se o username já existe
    for prof_data in PROFESSORES_MOCK.values():
        if prof_data['username'] == username:
            flash(f'O nome de usuário "{username}" já existe.', 'danger')
            return redirect(url_for('admin_gerenciar_professores'))

    new_prof_id = f"prof{len(PROFESSORES_MOCK) + 1:03d}" # Gera um ID simples
    PROFESSORES_MOCK[new_prof_id] = {
        "username": username,
        "senha": senha,
        "nome": nome,
        "disciplinas": disciplinas
    }
    flash(f'Professor {nome} adicionado com sucesso!', 'success')
    return redirect(url_for('admin_gerenciar_professores'))

@app.route('/admin/professores/edit/<professor_id>', methods=['GET'])
def admin_edit_professor_get(professor_id):
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))
    
    professor = PROFESSORES_MOCK.get(professor_id)
    if not professor:
        flash('Professor não encontrado.', 'danger')
        return redirect(url_for('admin_gerenciar_professores'))
    
    return render_template('admin_edit_professor.html', professor=professor, professor_id=professor_id)

@app.route('/admin/professores/edit/<professor_id>', methods=['POST'])
def admin_edit_professor_post(professor_id):
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))

    professor_original = PROFESSORES_MOCK.get(professor_id)
    if not professor_original:
        flash('Professor não encontrado.', 'danger')
        return redirect(url_for('admin_gerenciar_professores'))

    nome = request.form.get('nome')
    username = request.form.get('username')
    senha = request.form.get('senha') # Senha pode ser vazia para não alterar
    disciplinas_str = request.form.get('disciplinas', '')
    disciplinas = [d.strip() for d in disciplinas_str.split(',') if d.strip()]

    if not nome or not username:
        flash('Nome e usuário são obrigatórios.', 'danger')
        # Re-renderiza a página de edição com os dados atuais para correção
        return render_template('admin_edit_professor.html', professor=professor_original, professor_id=professor_id)
    
    # Verifica se o novo username já existe (e não é o username original do professor sendo editado)
    for prof_id_loop, prof_data in PROFESSORES_MOCK.items():
        if prof_id_loop != professor_id and prof_data['username'] == username:
            flash(f'O nome de usuário "{username}" já pertence a outro professor.', 'danger')
            return render_template('admin_edit_professor.html', professor=professor_original, professor_id=professor_id)

    PROFESSORES_MOCK[professor_id]['nome'] = nome
    PROFESSORES_MOCK[professor_id]['username'] = username
    if senha: # Altera a senha apenas se uma nova for fornecida
        PROFESSORES_MOCK[professor_id]['senha'] = senha
    PROFESSORES_MOCK[professor_id]['disciplinas'] = disciplinas
    
    flash(f'Professor {nome} atualizado com sucesso!', 'success')
    return redirect(url_for('admin_gerenciar_professores'))

@app.route('/admin/professores/delete/<professor_id>')
def admin_delete_professor(professor_id):
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))
    
    if professor_id in PROFESSORES_MOCK:
        del PROFESSORES_MOCK[professor_id]
        flash('Professor excluído com sucesso!', 'success')
    else:
        flash('Professor não encontrado.', 'danger')
    return redirect(url_for('admin_gerenciar_professores'))

# CRUD Alunos
@app.route('/admin/alunos')
def admin_gerenciar_alunos():
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))
    return render_template('admin_alunos.html', alunos_por_turma=ALUNOS_MOCK, turmas=TURMAS_MOCK, pais=PAIS_MOCK)

@app.route('/admin/alunos/add', methods=['POST'])
def admin_add_aluno():
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))

    nome_aluno = request.form.get('nome_aluno')
    turma_aluno = request.form.get('turma_aluno')
    pai_username_aluno = request.form.get('pai_username_aluno')

    if not nome_aluno or not turma_aluno or not pai_username_aluno:
        flash('Nome do aluno, turma e usuário do pai/responsável são obrigatórios.', 'danger')
        return redirect(url_for('admin_gerenciar_alunos'))
    
    if turma_aluno not in TURMAS_MOCK:
        flash(f'Turma "{turma_aluno}" inválida.', 'danger')
        return redirect(url_for('admin_gerenciar_alunos'))
    
    # Idealmente, verificar se o pai_username_aluno existe em PAIS_MOCK
    # if pai_username_aluno not in PAIS_MOCK:
    #     flash(f'Usuário do pai/responsável "{pai_username_aluno}" não encontrado.', 'danger')
    #     return redirect(url_for('admin_gerenciar_alunos'))

    new_aluno_id = f"aluno{uuid.uuid4().hex[:6]}" # Gera um ID único mais robusto
    novo_aluno_obj = {
        "id": new_aluno_id,
        "nome": nome_aluno,
        "pai_username": pai_username_aluno
    }

    if turma_aluno not in ALUNOS_MOCK:
        ALUNOS_MOCK[turma_aluno] = [] # Cria a lista se a turma for nova (embora deva existir em TURMAS_MOCK)
    ALUNOS_MOCK[turma_aluno].append(novo_aluno_obj)
    
    flash(f'Aluno {nome_aluno} adicionado à turma {turma_aluno} com sucesso!', 'success')
    return redirect(url_for('admin_gerenciar_alunos'))

@app.route('/admin/alunos/edit/<turma_original>/<aluno_id>', methods=['GET'])
def admin_edit_aluno_get(turma_original, aluno_id):
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))

    aluno_encontrado = None
    if turma_original in ALUNOS_MOCK:
        for al in ALUNOS_MOCK[turma_original]:
            if al['id'] == aluno_id:
                aluno_encontrado = al
                break
    
    if not aluno_encontrado:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('admin_gerenciar_alunos'))

    return render_template('admin_edit_aluno.html', 
                           aluno=aluno_encontrado, 
                           aluno_id=aluno_id, 
                           turma_original=turma_original, 
                           todas_turmas=TURMAS_MOCK)

@app.route('/admin/alunos/edit/<turma_original>/<aluno_id>', methods=['POST'])
def admin_edit_aluno_post(turma_original, aluno_id):
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))

    nome_aluno_novo = request.form.get('nome_aluno')
    turma_aluno_nova = request.form.get('turma_aluno')
    pai_username_novo = request.form.get('pai_username_aluno')

    if not nome_aluno_novo or not turma_aluno_nova or not pai_username_novo:
        flash('Nome do aluno, turma e usuário do pai/responsável são obrigatórios.', 'danger')
        # Para reenviar à página de edição, precisamos dos dados originais
        aluno_original_obj = None
        if turma_original in ALUNOS_MOCK:
            for al_obj in ALUNOS_MOCK[turma_original]:
                if al_obj['id'] == aluno_id:
                    aluno_original_obj = al_obj
                    break
        return render_template('admin_edit_aluno.html', 
                               aluno=aluno_original_obj, 
                               aluno_id=aluno_id, 
                               turma_original=turma_original, 
                               todas_turmas=TURMAS_MOCK)

    if turma_aluno_nova not in TURMAS_MOCK:
        flash(f'Nova turma "{turma_aluno_nova}" inválida.', 'danger')
        aluno_original_obj = None # Recarregar dados para o template
        if turma_original in ALUNOS_MOCK:
            for al_obj in ALUNOS_MOCK[turma_original]:
                if al_obj['id'] == aluno_id:
                    aluno_original_obj = al_obj
                    break
        return render_template('admin_edit_aluno.html', 
                               aluno=aluno_original_obj, 
                               aluno_id=aluno_id, 
                               turma_original=turma_original, 
                               todas_turmas=TURMAS_MOCK)

    # Remover aluno da turma original
    aluno_movido = None
    if turma_original in ALUNOS_MOCK:
        for i, al in enumerate(ALUNOS_MOCK[turma_original]):
            if al['id'] == aluno_id:
                aluno_movido = ALUNOS_MOCK[turma_original].pop(i)
                break
    
    if not aluno_movido:
        flash('Erro ao encontrar aluno para edição.', 'danger')
        return redirect(url_for('admin_gerenciar_alunos'))

    # Atualizar dados do aluno
    aluno_movido['nome'] = nome_aluno_novo
    aluno_movido['pai_username'] = pai_username_novo

    # Adicionar à nova turma
    if turma_aluno_nova not in ALUNOS_MOCK:
        ALUNOS_MOCK[turma_aluno_nova] = []
    ALUNOS_MOCK[turma_aluno_nova].append(aluno_movido)

    flash(f'Aluno {nome_aluno_novo} atualizado com sucesso!', 'success')
    return redirect(url_for('admin_gerenciar_alunos'))

@app.route('/admin/alunos/delete/<turma>/<aluno_id>')
def admin_delete_aluno(turma, aluno_id):
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))

    aluno_removido = False
    if turma in ALUNOS_MOCK:
        for i, al in enumerate(ALUNOS_MOCK[turma]):
            if al['id'] == aluno_id:
                del ALUNOS_MOCK[turma][i]
                aluno_removido = True
                break
    
    if aluno_removido:
        flash('Aluno excluído com sucesso!', 'success')
    else:
        flash('Aluno não encontrado.', 'danger')
    return redirect(url_for('admin_gerenciar_alunos'))

# CRUD Turmas
@app.route('/admin/turmas')
def admin_gerenciar_turmas():
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))
    return render_template('admin_turmas.html', turmas=TURMAS_MOCK)

@app.route('/admin/turmas/add', methods=['POST'])
def admin_add_turma():
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))
    
    nome_turma = request.form.get('nome_turma')
    if not nome_turma:
        flash('Nome da turma é obrigatório.', 'danger')
        return redirect(url_for('admin_gerenciar_turmas'))
    
    if nome_turma in TURMAS_MOCK:
        flash(f'Turma "{nome_turma}" já existe.', 'danger')
    else:
        TURMAS_MOCK.append(nome_turma)
        ALUNOS_MOCK[nome_turma] = [] # Inicializa a lista de alunos para a nova turma
        flash(f'Turma "{nome_turma}" adicionada com sucesso!', 'success')
    return redirect(url_for('admin_gerenciar_turmas'))

@app.route('/admin/turmas/delete/<nome_turma>')
def admin_delete_turma(nome_turma):
    if session.get('user_type') != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_admin_get'))

    if nome_turma in TURMAS_MOCK:
        # Verificar se a turma está vazia antes de excluir
        if ALUNOS_MOCK.get(nome_turma):
            flash(f'Não é possível excluir a turma "{nome_turma}" pois ela contém alunos. Remova os alunos primeiro.', 'danger')
            return redirect(url_for('admin_gerenciar_turmas'))
        
        TURMAS_MOCK.remove(nome_turma)
        if nome_turma in ALUNOS_MOCK: # Remove também do dict de alunos
            del ALUNOS_MOCK[nome_turma]
        flash(f'Turma "{nome_turma}" excluída com sucesso!', 'success')
    else:
        flash(f'Turma "{nome_turma}" não encontrada.', 'danger')
    return redirect(url_for('admin_gerenciar_turmas'))


# --- ROTAS GERAIS E DE PROFESSORES (continuação) ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login_professores', methods=['GET'])
def login_professores_get():
    return render_template('login_professores.html')

@app.route('/login_professores', methods=['POST'])
def login_professores_post():
    submitted_username = request.form.get('username')
    submitted_password = request.form.get('password')
    
    professor_encontrado = None
    professor_id_encontrado = None
    for prof_id, prof_data in PROFESSORES_MOCK.items():
        if prof_data['username'] == submitted_username and prof_data['senha'] == submitted_password:
            professor_encontrado = prof_data
            professor_id_encontrado = prof_id
            break

    if professor_encontrado:
        session['user_type'] = 'professor'
        session['username'] = submitted_username
        session['professor_id'] = professor_id_encontrado
        session['nome_display'] = professor_encontrado['nome']
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard_professor'))
    else:
        flash('Usuário ou senha inválidos.', 'danger')
        return redirect(url_for('login_professores_get'))

@app.route('/dashboard_professor')
def dashboard_professor():
    if session.get('user_type') == 'professor':
        return render_template('dashboard_professor.html', 
                              notas_lancadas=NOTAS_GLOBAIS, 
                              turmas=TURMAS_MOCK, 
                              alunos_por_turma=ALUNOS_MOCK)
    flash('Você precisa estar logado como professor para acessar esta página.', 'info')
    return redirect(url_for('login_professores_get'))

@app.route('/lancar_nota', methods=['POST'])
def lancar_nota():
    global NOTAS_GLOBAIS
    
    if session.get('user_type') != 'professor':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login_professores_get'))

    turma = request.form.get('turma')
    aluno_id = request.form.get('aluno')
    disciplina = request.form.get('disciplina')
    nota_valor = request.form.get('nota')
    periodo = request.form.get('periodo')

    nome_aluno = "Desconhecido"
    if turma in ALUNOS_MOCK:
        for aluno_info in ALUNOS_MOCK[turma]:
            if aluno_info['id'] == aluno_id:
                nome_aluno = aluno_info['nome']
                break
    
    if not all([turma, aluno_id, disciplina, nota_valor, periodo]):
        flash('Todos os campos são obrigatórios para lançar a nota.', 'danger')
        return redirect(url_for('dashboard_professor'))

    try:
        nota_float = float(nota_valor)
        if not (0 <= nota_float <= 10):
            raise ValueError("Nota fora do intervalo permitido")
    except ValueError:
        flash('Valor da nota inválido. Use números entre 0 e 10.', 'danger')
        return redirect(url_for('dashboard_professor'))

    nova_nota = {
        'turma': turma,
        'aluno': nome_aluno,
        'aluno_id': aluno_id,
        'disciplina': disciplina,
        'nota': nota_float,
        'periodo': periodo,
        'professor_que_lancou': session.get('username')
    }

    NOTAS_GLOBAIS.append(nova_nota)

    flash(f'Nota para {nome_aluno} em {disciplina} ({periodo}) lançada com sucesso!', 'success')
    return redirect(url_for('dashboard_professor'))

# --- ROTAS PARA PAIS ---
@app.route('/login_pais', methods=['GET'])
def login_pais_get():
    return render_template('login_pais.html')

@app.route('/login_pais', methods=['POST'])
def login_pais_post():
    username_pai = request.form.get('username_pai')
    password_pai = request.form.get('password_pai')
    pai_info = PAIS_MOCK.get(username_pai)

    if pai_info and pai_info['senha'] == password_pai:
        session['user_type'] = 'pai'
        session['username_pai'] = username_pai
        session['nome_display_pai'] = pai_info['nome']
        session['filho_id'] = pai_info['filho_id']
        
        aluno_nome_display = "Não encontrado"
        aluno_turma_display = "Não encontrada"
        for turma, alunos_lista in ALUNOS_MOCK.items():
            for aluno_obj in alunos_lista:
                if aluno_obj['id'] == pai_info['filho_id']:
                    aluno_nome_display = aluno_obj['nome']
                    aluno_turma_display = turma
                    break
            if aluno_nome_display != "Não encontrado":
                break
        session['nome_aluno'] = aluno_nome_display
        session['turma_aluno'] = aluno_turma_display

        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard_pais'))
    else:
        flash('Usuário ou senha inválidos.', 'danger')
        return redirect(url_for('login_pais_get'))

@app.route('/dashboard_pais')
def dashboard_pais():
    global NOTAS_GLOBAIS
    
    if session.get('user_type') == 'pai':
        filho_id_logado = session.get('filho_id')
        notas_do_aluno = [nota for nota in NOTAS_GLOBAIS if nota.get('aluno_id') == filho_id_logado]
        
        return render_template('dashboard_pais.html', 
                               notas_aluno=notas_do_aluno,
                               nome_aluno=session.get('nome_aluno'),
                               turma_aluno=session.get('turma_aluno'))
    flash('Você precisa estar logado como pai/responsável para acessar esta página.', 'info')
    return redirect(url_for('login_pais_get'))

# --- ROTA DE LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('user_type', None)
    session.pop('username', None)
    session.pop('professor_id', None)
    session.pop('nome_display', None)
    session.pop('username_pai', None)
    session.pop('nome_display_pai', None)
    session.pop('filho_id', None)
    session.pop('nome_aluno', None)
    session.pop('turma_aluno', None)
    session.pop('admin_username', None) 
    session.pop('nome_display_admin', None) 
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    NOTAS_GLOBAIS = [
        {
            'turma': '6A',
            'aluno': 'João Silva',
            'aluno_id': 'aluno1_id',
            'disciplina': 'Matemática',
            'nota': 8.5,
            'periodo': '1º Bimestre',
            'professor_que_lancou': 'professor1'
        },
        {
            'turma': '6A',
            'aluno': 'João Silva',
            'aluno_id': 'aluno1_id',
            'disciplina': 'Português',
            'nota': 7.8,
            'periodo': '1º Bimestre',
            'professor_que_lancou': 'professor2'
        },
        {
            'turma': '6A',
            'aluno': 'Maria Oliveira',
            'aluno_id': 'aluno2_id',
            'disciplina': 'Matemática',
            'nota': 9.2,
            'periodo': '1º Bimestre',
            'professor_que_lancou': 'professor1'
        }
    ]
    app.run(host='0.0.0.0', port=5000, debug=True)



# --- ROTAS DO MÓDULO FINANCEIRO (PAIS) ---
@app.route("/visualizar_financeiro_do_pai", endpoint="visualizar_financeiro_do_pai")
def visualizar_financeiro_do_pai():
    if session.get("user_type") != "pai":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_pais_get"))

    pai_username = session.get("username_pai")
    pai_info = PAIS_MOCK.get(pai_username)
    if not pai_info:
        flash("Informações do responsável não encontradas.", "danger")
        return redirect(url_for("login_pais_get"))

    aluno_id = pai_info.get("filho_id")
    aluno_nome = ""
    # Encontrar nome do aluno
    for turma, alunos_na_turma in ALUNOS_MOCK.items():
        for aluno in alunos_na_turma:
            if aluno["id"] == aluno_id:
                aluno_nome = aluno["nome"]
                break
        if aluno_nome:
            break
    
    mensalidades_aluno = []
    for mensalidade_id, detalhes_mensalidade in MENSALIDADES_MOCK.items():
        if detalhes_mensalidade["id_aluno"] == aluno_id:
            # Verificar se está vencida
            if detalhes_mensalidade["status"] == "Pendente":
                try:
                    data_vencimento = datetime.datetime.strptime(detalhes_mensalidade["data_vencimento"], "%Y-%m-%d").date()
                    if data_vencimento < datetime.date.today():
                        detalhes_mensalidade["status"] = "Vencido"
                except ValueError:
                    pass # Mantém pendente se a data for inválida
            mensalidades_aluno.append(detalhes_mensalidade)
    
    # Ordenar por data de vencimento (mais recentes primeiro, por exemplo)
    mensalidades_aluno.sort(key=lambda m: m["data_vencimento"], reverse=True)

    return render_template("dashboard_pais_financeiro.html", 
                           mensalidades_aluno=mensalidades_aluno, 
                           aluno_nome=aluno_nome)

@app.route("/gerar_boleto_simulado/<id_mensalidade>", methods=["POST"])
def gerar_boleto_simulado(id_mensalidade):
    if session.get("user_type") != "pai":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_pais_get"))

    mensalidade = MENSALIDADES_MOCK.get(id_mensalidade)
    if not mensalidade:
        flash("Mensalidade não encontrada.", "danger")
        return redirect(url_for("visualizar_financeiro_do_pai"))

    # Verificar se o pai logado é o responsável pelo aluno da mensalidade
    pai_username = session.get("username_pai")
    pai_info = PAIS_MOCK.get(pai_username)
    aluno_id_pai = pai_info.get("filho_id")

    if mensalidade.get("id_aluno") != aluno_id_pai:
        flash("Acesso não autorizado a esta mensalidade.", "danger")
        return redirect(url_for("visualizar_financeiro_do_pai"))

    # Simular geração de boleto
    codigo_boleto = f"simulado_{id_mensalidade}_{uuid.uuid4().hex[:8]}"
    MENSALIDADES_MOCK[id_mensalidade]["codigo_boleto_simulado"] = codigo_boleto
    MENSALIDADES_MOCK[id_mensalidade]["link_boleto_simulado"] = url_for("ver_boleto_simulado_get", nome_arquivo_boleto=codigo_boleto) # Apenas para referência interna
    
    # Dados para o template do boleto
    aluno_info = None
    for turma_alunos in ALUNOS_MOCK.values():
        for al in turma_alunos:
            if al["id"] == mensalidade["id_aluno"]:
                aluno_info = al
                break
        if aluno_info: break

    data_emissao = datetime.date.today().strftime("%Y-%m-%d")
    nosso_numero = f"{datetime.date.today().year}{id_mensalidade[-5:]}{uuid.uuid4().hex[:3]}".upper()
    linha_digitavel = f"{uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} 1 {mensalidade['valor']:.2f}".replace(".","")
    codigo_barras_num = f"00191{mensalidade['valor']:.2f}{nosso_numero}{data_emissao.replace('-','')}{uuid.uuid4().hex[:10]}".replace(".","")

    flash('Boleto simulado gerado. Você pode "confirmar o pagamento" abaixo.', "info")
    return render_template("boleto_simulado.html", 
                           mensalidade=mensalidade, 
                           aluno_info=aluno_info, 
                           pai_info=pai_info,
                           data_emissao_simulada=data_emissao,
                           nosso_numero_simulado=nosso_numero,
                           linha_digitavel_simulada=linha_digitavel,
                           codigo_barras_simulado=codigo_barras_num)

@app.route("/ver_boleto_simulado/<nome_arquivo_boleto>") # GET por padrão
def ver_boleto_simulado_get(nome_arquivo_boleto):
    # Encontrar a mensalidade pelo codigo_boleto_simulado
    mensalidade_encontrada = None
    id_mensalidade_ref = None
    for id_mens, mens_data in MENSALIDADES_MOCK.items():
        if mens_data.get("codigo_boleto_simulado") == nome_arquivo_boleto:
            mensalidade_encontrada = mens_data
            id_mensalidade_ref = id_mens
            break
    
    if not mensalidade_encontrada:
        flash("Boleto simulado não encontrado.", "danger")
        # Redirecionar para o painel apropriado dependendo do tipo de usuário
        if session.get("user_type") == "pai":
            return redirect(url_for("visualizar_financeiro_do_pai"))
        elif session.get("user_type") == "admin":
            return redirect(url_for("admin_gerenciar_mensalidades"))
        else:
            return redirect(url_for("home")) # Fallback

    # Verificar permissão de acesso
    acesso_permitido = False
    if session.get("user_type") == "admin":
        acesso_permitido = True
    elif session.get("user_type") == "pai":
        pai_username = session.get("username_pai")
        pai_info_atual = PAIS_MOCK.get(pai_username)
        if pai_info_atual and pai_info_atual.get("filho_id") == mensalidade_encontrada.get("id_aluno"):
            acesso_permitido = True
    
    if not acesso_permitido:
        flash("Acesso não autorizado a este boleto.", "danger")
        if session.get("user_type") == "pai":
            return redirect(url_for("visualizar_financeiro_do_pai"))
        else:
            return redirect(url_for("home"))

    # Dados para o template do boleto
    aluno_info = None
    for turma_alunos in ALUNOS_MOCK.values():
        for al in turma_alunos:
            if al["id"] == mensalidade_encontrada["id_aluno"]:
                aluno_info = al
                break
        if aluno_info: break
    
    pai_do_aluno_info = None
    if aluno_info and aluno_info.get("pai_username"):
        pai_do_aluno_info = PAIS_MOCK.get(aluno_info.get("pai_username"))

    data_emissao = datetime.date.today().strftime("%Y-%m-%d") # Pode ser a data de geração original se armazenada
    nosso_numero = f"{datetime.date.today().year}{id_mensalidade_ref[-5:]}{uuid.uuid4().hex[:3]}".upper()
    linha_digitavel = f"{uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} {uuid.uuid4().hex[:5]} 1 {mensalidade_encontrada['valor']:.2f}".replace(".","")
    codigo_barras_num = f"00191{mensalidade_encontrada['valor']:.2f}{nosso_numero}{data_emissao.replace('-','')}{uuid.uuid4().hex[:10]}".replace(".","")

    return render_template("boleto_simulado.html", 
                           mensalidade=mensalidade_encontrada, 
                           aluno_info=aluno_info, 
                           pai_info=pai_do_aluno_info,
                           data_emissao_simulada=data_emissao,
                           nosso_numero_simulado=nosso_numero,
                           linha_digitavel_simulada=linha_digitavel,
                           codigo_barras_simulado=codigo_barras_num)

@app.route("/registrar_pagamento_simulado/<id_mensalidade>", methods=["POST"])
def registrar_pagamento_simulado(id_mensalidade):
    if session.get("user_type") != "pai":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_pais_get"))

    mensalidade = MENSALIDADES_MOCK.get(id_mensalidade)
    if not mensalidade:
        flash("Mensalidade não encontrada.", "danger")
        return redirect(url_for("visualizar_financeiro_do_pai"))

    # Verificar se o pai logado é o responsável
    pai_username = session.get("username_pai")
    pai_info = PAIS_MOCK.get(pai_username)
    if mensalidade.get("id_aluno") != pai_info.get("filho_id"):
        flash("Acesso não autorizado a esta mensalidade.", "danger")
        return redirect(url_for("visualizar_financeiro_do_pai"))

    if mensalidade["status"] == "Pago":
        flash("Esta mensalidade já foi paga.", "info")
        return redirect(url_for("visualizar_financeiro_do_pai"))

    MENSALIDADES_MOCK[id_mensalidade]["status"] = "Em Processamento"
    # MENSALIDADES_MOCK[id_mensalidade]["data_pagamento"] = datetime.date.today().strftime("%Y-%m-%d") # Gestor confirma
    flash("Pagamento simulado registrado! Aguardando confirmação da escola.", "success")
    return redirect(url_for("visualizar_financeiro_do_pai"))


# --- ROTAS DO MÓDULO FINANCEIRO (ADMIN) ---
@app.route("/admin/mensalidades")
def admin_gerenciar_mensalidades():
    if session.get("user_type") != "admin":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_admin_get"))

    # Coletar todos os alunos para exibir nomes e turmas
    alunos_details = {}
    for turma, alunos_na_turma in ALUNOS_MOCK.items():
        for aluno in alunos_na_turma:
            alunos_details[aluno["id"]] = {"nome": aluno["nome"], "turma": turma, "pai_username": aluno.get("pai_username")}

    mensalidades_filtradas = list(MENSALIDADES_MOCK.values())

    # Aplicar filtros
    filtro_aluno_nome = request.args.get("filtro_aluno_nome", "").strip().lower()
    filtro_turma = request.args.get("filtro_turma", "").strip()
    filtro_status = request.args.get("filtro_status", "").strip()

    if filtro_aluno_nome:
        mensalidades_filtradas = [m for m in mensalidades_filtradas if m["id_aluno"] in alunos_details and filtro_aluno_nome in alunos_details[m["id_aluno"]]["nome"].lower()]
    
    if filtro_turma:
        mensalidades_filtradas = [m for m in mensalidades_filtradas if m["id_aluno"] in alunos_details and alunos_details[m["id_aluno"]]["turma"] == filtro_turma]

    if filtro_status:
        mensalidades_filtradas = [m for m in mensalidades_filtradas if m["status"] == filtro_status]
        
    # Atualizar status para Vencido se aplicável
    for m in mensalidades_filtradas:
        if m["status"] == "Pendente":
            try:
                data_vencimento = datetime.datetime.strptime(m["data_vencimento"], "%Y-%m-%d").date()
                if data_vencimento < datetime.date.today():
                    m["status"] = "Vencido"
            except ValueError:
                pass 

    return render_template("admin_gerenciar_mensalidades.html", 
                           mensalidades_list=mensalidades_filtradas, 
                           alunos_details=alunos_details,
                           todas_turmas=TURMAS_MOCK)

@app.route("/admin/mensalidades/add", methods=["GET"])
def admin_add_mensalidade_get():
    if session.get("user_type") != "admin":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_admin_get"))
    
    # Coletar todos os alunos para o dropdown
    todos_alunos_list = []
    for turma, alunos_na_turma in ALUNOS_MOCK.items():
        for aluno in alunos_na_turma:
            todos_alunos_list.append({"id": aluno["id"], "nome": aluno["nome"], "turma": turma})
    todos_alunos_list.sort(key=lambda x: x["nome"]) # Ordenar por nome

    return render_template("admin_add_mensalidade.html", todos_alunos=todos_alunos_list)

@app.route("/admin/mensalidades/add", methods=["POST"])
def admin_add_mensalidade_post():
    if session.get("user_type") != "admin":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_admin_get"))

    id_aluno = request.form.get("id_aluno")
    mes_referencia = request.form.get("mes_referencia") # Formato YYYY-MM
    valor_str = request.form.get("valor")
    data_vencimento = request.form.get("data_vencimento") # Formato YYYY-MM-DD

    if not all([id_aluno, mes_referencia, valor_str, data_vencimento]):
        flash("Todos os campos são obrigatórios.", "danger")
        return redirect(url_for("admin_add_mensalidade_get"))
    
    try:
        valor = float(valor_str)
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")
    except ValueError:
        flash("Valor da mensalidade inválido.", "danger")
        return redirect(url_for("admin_add_mensalidade_get"))

    # Validar formato das datas (simplesmente para o mock)
    try:
        datetime.datetime.strptime(mes_referencia + "-01", "%Y-%m-%d") # Adiciona dia para validar mês/ano
        datetime.datetime.strptime(data_vencimento, "%Y-%m-%d")
    except ValueError:
        flash("Formato de Mês de Referência (AAAA-MM) ou Data de Vencimento (AAAA-MM-DD) inválido.", "danger")
        return redirect(url_for("admin_add_mensalidade_get"))

    new_mensalidade_id = f"mensalidade{uuid.uuid4().hex[:6]}"
    MENSALIDADES_MOCK[new_mensalidade_id] = {
        "id_mensalidade": new_mensalidade_id,
        "id_aluno": id_aluno,
        "mes_referencia": mes_referencia,
        "valor": valor,
        "data_vencimento": data_vencimento,
        "status": "Pendente",
        "data_pagamento": None,
        "codigo_boleto_simulado": None,
        "link_boleto_simulado": None
    }
    flash("Nova mensalidade adicionada com sucesso!", "success")
    return redirect(url_for("admin_gerenciar_mensalidades"))

@app.route("/admin/mensalidades/confirmar_pagamento/<id_mensalidade>", methods=["POST"])
def admin_confirmar_pagamento_mensalidade(id_mensalidade):
    if session.get("user_type") != "admin":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_admin_get"))

    mensalidade = MENSALIDADES_MOCK.get(id_mensalidade)
    if not mensalidade:
        flash("Mensalidade não encontrada.", "danger")
        return redirect(url_for("admin_gerenciar_mensalidades"))

    MENSALIDADES_MOCK[id_mensalidade]["status"] = "Pago"
    MENSALIDADES_MOCK[id_mensalidade]["data_pagamento"] = datetime.date.today().strftime("%Y-%m-%d")
    flash(f"Pagamento da mensalidade {id_mensalidade} confirmado.", "success")
    return redirect(url_for("admin_gerenciar_mensalidades"))

@app.route("/admin/mensalidades/alterar_vencimento/<id_mensalidade>", methods=["POST"])
def admin_alterar_vencimento_mensalidade(id_mensalidade):
    if session.get("user_type") != "admin":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_admin_get"))

    nova_data_vencimento = request.form.get("nova_data_vencimento")
    if not nova_data_vencimento:
        flash("Nova data de vencimento é obrigatória.", "danger")
        return redirect(url_for("admin_gerenciar_mensalidades"))
    
    try:
        datetime.datetime.strptime(nova_data_vencimento, "%Y-%m-%d")
    except ValueError:
        flash("Formato da nova data de vencimento (AAAA-MM-DD) inválido.", "danger")
        return redirect(url_for("admin_gerenciar_mensalidades"))

    mensalidade = MENSALIDADES_MOCK.get(id_mensalidade)
    if not mensalidade:
        flash("Mensalidade não encontrada.", "danger")
        return redirect(url_for("admin_gerenciar_mensalidades"))

    MENSALIDADES_MOCK[id_mensalidade]["data_vencimento"] = nova_data_vencimento
    # Se estava vencida e a nova data é futura, volta para pendente
    if mensalidade["status"] == "Vencido":
        if datetime.datetime.strptime(nova_data_vencimento, "%Y-%m-%d").date() >= datetime.date.today():
            MENSALIDADES_MOCK[id_mensalidade]["status"] = "Pendente"
            
    flash(f"Data de vencimento da mensalidade {id_mensalidade} alterada para {nova_data_vencimento}.", "success")
    return redirect(url_for("admin_gerenciar_mensalidades"))




# --- ROTA DE TESTE FINANCEIRO PAI ---
@app.route("/teste_rota_financeira_pai_nova", endpoint="teste_rota_financeira_pai_nova")
def teste_rota_financeira_pai_nova():
    if session.get("user_type") != "pai":
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("login_pais_get"))
    return render_template("teste_financeiro_pai.html")


