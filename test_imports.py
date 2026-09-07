"""
Script para testar importações localmente antes do deploy
Execute este script para verificar se todas as importações funcionam
"""
import sys
import os

print("=" * 50)
print("TESTE DE IMPORTACOES - FinTrack BFF")
print("=" * 50)

# Configurar path como na Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"\n[DIRETORIO] Atual: {current_dir}")
print(f"[DIRETORIO] Pai: {parent_dir}")
print(f"[PYTHON] Path: {sys.path[:3]}")

print("\n" + "=" * 50)
print("TESTANDO IMPORTACOES BASICAS")
print("=" * 50)

# Testar Flask
try:
    from flask import Flask
    print("[OK] Flask importado com sucesso")
except ImportError as e:
    print(f"[ERRO] Flask: {e}")
    sys.exit(1)

# Testar Flask-CORS
try:
    from flask_cors import CORS
    print("[OK] Flask-CORS importado com sucesso")
except ImportError as e:
    print(f"[ERRO] Flask-CORS: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("TESTANDO IMPORTACOES DO PROJETO")
print("=" * 50)

# Testar routes
try:
    from routes.expenses import expenses_bp
    print("[OK] routes.expenses importado com sucesso")
except ImportError as e:
    print(f"[ERRO] routes.expenses: {e}")

try:
    from routes.dashboard import dashboard_bp
    print("[OK] routes.dashboard importado com sucesso")
except ImportError as e:
    print(f"[ERRO] routes.dashboard: {e}")

try:
    from routes.upload import upload_bp
    print("[OK] routes.upload importado com sucesso")
except ImportError as e:
    print(f"[ERRO] routes.upload: {e}")

try:
    from routes.analytics import analytics_bp
    print("[OK] routes.analytics importado com sucesso")
except ImportError as e:
    print(f"[ERRO] routes.analytics: {e}")

try:
    from routes.reports import reports_bp
    print("[OK] routes.reports importado com sucesso")
except ImportError as e:
    print(f"[ERRO] routes.reports: {e}")

# Testar services
try:
    from services.expense_service import ExpenseService
    print("[OK] services.expense_service importado com sucesso")
except ImportError as e:
    print(f"[ERRO] services.expense_service: {e}")

try:
    from services.dashboard_service import DashboardService
    print("[OK] services.dashboard_service importado com sucesso")
except ImportError as e:
    print(f"[ERRO] services.dashboard_service: {e}")

try:
    from services.ocr_service import OCRService
    print("[OK] services.ocr_service importado com sucesso")
except ImportError as e:
    print(f"[ERRO] services.ocr_service: {e}")

# Testar database
try:
    from database.db import get_db_connection, init_db
    print("[OK] database.db importado com sucesso")
except ImportError as e:
    print(f"[ERRO] database.db: {e}")

# Testar schemas
try:
    from schemas.expense import ExpenseResponse
    print("[OK] schemas.expense importado com sucesso")
except ImportError as e:
    print(f"[ERRO] schemas.expense: {e}")

try:
    from schemas.dashboard import DashboardSummary
    print("[OK] schemas.dashboard importado com sucesso")
except ImportError as e:
    print(f"[ERRO] schemas.dashboard: {e}")

try:
    from schemas.upload import UploadResponse
    print("[OK] schemas.upload importado com sucesso")
except ImportError as e:
    print(f"[ERRO] schemas.upload: {e}")

# Testar config
try:
    from config import Config
    print("[OK] config importado com sucesso")
except ImportError as e:
    print(f"[ERRO] config: {e}")

print("\n" + "=" * 50)
print("TESTANDO CRIACAO DA APP FLASK")
print("=" * 50)

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def test():
        return jsonify({'status': 'ok'})
    
    print("[OK] App Flask criada com sucesso")
    
    # Testar registro de blueprints
    try:
        from routes.expenses import expenses_bp
        app.register_blueprint(expenses_bp, url_prefix='/api/v1')
        print("[OK] Blueprint expenses registrado com sucesso")
    except Exception as e:
        print(f"[ERRO] Blueprint: {e}")
    
except Exception as e:
    print(f"[ERRO] App Flask: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("RESUMO DO TESTE")
print("=" * 50)
print("Se todas as importacoes funcionaram, o problema pode ser:")
print("1. Variaveis de ambiente na Vercel")
print("2. Conexao com banco de dados")
print("3. Timeout de execucao")
print("4. Permissoes de arquivo")
print("\nSe houve erros de importacao, verifique:")
print("1. Estrutura de pastas")
print("2. requirements.txt completo")
print("3. Caminhos relativos corretos")
print("=" * 50)
