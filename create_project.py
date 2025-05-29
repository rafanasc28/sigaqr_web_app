import os

def create_project_structure():
    # Estrutura corrigida
    project_items = [
        ('app', [
            ('templates', [
                'base.html',
                'generate.html',
                'read.html',
                'dashboard.html'
            ]),
            ('static', [
                ('css', ['style.css']),
                ('js', ['scanner.js', 'generator.js']),
                ('uploads', [])
            ]),
            ('models', ['asset.py', 'validators.py']),
            ('routes', ['__init__.py', 'main_routes.py', 'api_routes.py']),
            ('utils', ['database.py', 'qr_handler.py']),
            '__init__.py'
        ]),
        ('tests', [
            'test_routes.py',
            'test_models.py'
        ]),
        ('migrations', []),
        'requirements.txt',
        'run.py',
        'config.py',
        '.env',
        'firebird_setup.sql'
    ]

    def create_folder(path):
        try:
            os.makedirs(path)
            print(f"✓ Pasta criada: {path}")
        except FileExistsError:
            print(f"⚠ Pasta já existe: {path}")

    def create_file(path, file_content=None):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                if file_content:
                    f.write(file_content)
            print(f"✓ Arquivo criado: {path}")
        except FileExistsError:
            print(f"⚠ Arquivo já existe: {path}")

    def build_tree(base_path, items):
        for item in items:
            if isinstance(item, tuple):
                folder, children = item
                current_path = os.path.join(base_path, folder)
                create_folder(current_path)
                build_tree(current_path, children)
            else:
                if '.' in item:
                    create_file(os.path.join(base_path, item))
                else:
                    create_folder(os.path.join(base_path, item))

    # Conteúdo dos arquivos (mesmo da versão anterior)
    initial_content = {
        # ... (manter o mesmo conteúdo do script anterior)
    }

    # Criar estrutura a partir da raiz 'siga_web'
    root_folder = 'siga_web'
    create_folder(root_folder)
    build_tree(root_folder, project_items)

    # Criar arquivos principais
    for file_name, content in initial_content.items():
        file_path = os.path.join(root_folder, file_name)
        create_file(file_path, content)

    print("\n✅ Estrutura criada corretamente!")
    print(f"Local: {os.path.abspath(root_folder)}")

if __name__ == '__main__':
    create_project_structure()