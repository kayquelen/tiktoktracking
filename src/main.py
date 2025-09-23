import os
import sys
from dotenv import load_dotenv

# Garante que o diretório raiz do projeto esteja no PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Carrega variáveis de ambiente
load_dotenv()

# Importa app e db do main.py da raiz, mantendo compatibilidade
from main import app, db  # noqa: E402

if __name__ == '__main__':
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', '5000'))
    debug = os.getenv('APP_ENV', 'development') == 'development'
    app.run(host=host, port=port, debug=debug)
