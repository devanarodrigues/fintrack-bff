"""
Script para testar importações localmente antes do deploy
Execute este script para verificar se todas as importações funcionam
"""
import sys
import os

print("=" * 50)
print("TESTE DE IMPORTAÇÕES - FinTrack BFF")
print("=" * 50)

# Configurar path como na Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"\n📁 Diretório atual: {current_dir}")
print(f"📁 Diretório pai: {parent_dir}")
print(f"📁 Python path: {sys.path[:3]}")

print("\n" + "=" * 50)
print("TESTANDO IMPORTAÇÕES BÁSICAS")
print("=" * 50)

# Testar Flask
try:
    from flask import Flask
    print("✅ Flask importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Flask: {e}")
    sys.exit(1)

# Testar Flask-CORS
try:
    from flask_cors import CORS
    print("✅ Flask-CORS importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Flask-CORS: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("TESTANDO IMPORTAÇÕES DO PROJETO")
print("=" * 50)

# Testar routes
try:
    from routes.expenses import expenses_bp
    print("✅ routes.expenses importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar routes.expenses: {e}")

try:
    from routes.dashboard import dashboard_bp
    print("✅ routes.dashboard importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar routes.dashboard: {e}")

try:
    from routes.upload import upload_bp
    print("✅ routes.upload importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar routes.upload: {e}")

try:
    from routes.analytics import analytics_bp
    print("✅ routes.analytics importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar routes.analytics: {e}")

try:
    from routes.reports import reports_bp
    print("✅ routes.reports importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar routes.reports: {e}")

# Testar services
try:
    from services.expense_service import ExpenseService
    print("✅ services.expense_service importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar services.expense_service: {e}")

try:
    from services.dashboard_service import DashboardService
    print("✅ services.dashboard_service importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar services.dashboard_service: {e}")

try:
    from services.ocr_service import OCRService
    print("✅ services.ocr_service importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar services.ocr_service: {e}")

# Testar database
try:
    from database.db import get_db_connection, init_db
    print("✅ database.db importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar database.db: {e}")

# Testar schemas
try:
    from schemas.expense import ExpenseResponse
    print("✅ schemas.expense importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar schemas.expense: {e}")

try:
    from schemas.dashboard import DashboardSummary
    print("✅ schemas.dashboard importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar schemas.dashboard: {e}")

try:
    from schemas.upload import UploadResponse
    print("✅ schemas.upload importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar schemas.upload: {e}")

# Testar config
try:
    from config import Config
    print("✅ config importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar config: {e}")

print("\n" + "=" * 50)
print("TESTANDO CRIAÇÃO DA APP FLASK")
print("=" * 50)

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def test():
        return jsonify({'status': 'ok'})
    
    print("✅ App Flask criada com sucesso")
    
    # Testar registro de blueprints
    try:
        from routes.expenses import expenses_bp
        app.register_blueprint(expenses_bp, url_prefix='/api/v1')
        print("✅ Blueprint expenses registrado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao registrar blueprint: {e}")
    
except Exception as e:
    print(f"❌ Erro ao criar app Flask: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("RESUMO DO TESTE")
print("=" * 50)
print("Se todas as importações funcionaram, o problema pode ser:")
print("1. Variáveis de ambiente na Vercel")
print("2. Conexão com banco de dados")
print("3. Timeout de execução")
print("4. Permissões de arquivo")
print("\nSe houve erros de importação, verifique:")
print("1. Estrutura de pastas")
print("2. requirements.txt completo")
print("3. Caminhos relativos corretos")
print("=" * 50)
