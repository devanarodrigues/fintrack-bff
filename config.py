"""
Configurações da aplicação FinTrack BFF
Este arquivo contém as configurações de conexão com o banco de dados PostgreSQL
Adaptado para funcionar em ambiente Vercel serverless
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env (apenas em desenvolvimento)
# Em produção na Vercel, as variáveis de ambiente são injetadas automaticamente
if os.getenv('VERCEL') != '1':
    load_dotenv()

# Detectar se está rodando na Vercel (antes da classe para evitar NameError)
IS_VERCEL = os.getenv('VERCEL') == '1'

class Config:
    """Configurações da aplicação"""
    
    # Detectar se está rodando na Vercel
    IS_VERCEL = IS_VERCEL
    
    # Configurações do Banco de Dados PostgreSQL
    # Na Vercel, pode usar Supabase ou outro banco PostgreSQL gerenciado
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'fintrack')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    # URL de conexão com o banco de dados
    @staticmethod
    def get_database_url():
        """Retorna a URL de conexão com o banco de dados PostgreSQL
        
        Força IPv4 para evitar problemas de conexão IPv6 na Vercel
        """
        # Forçar uso de IPv4 adicionando parâmetro hostaddr
        # Isso resolve problemas de conexão IPv6 na Vercel
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?hostaddr={Config.DB_HOST}"
    
    # Configurações da API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5000'))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Configurações de Upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    # Na Vercel, usar /tmp para arquivos temporários
    # Mas na Vercel Integration, pode vir como ./uploads, então corrigir
    upload_folder_env = os.getenv('UPLOAD_FOLDER')
    if IS_VERCEL:
        # Forçar /tmp na Vercel
        UPLOAD_FOLDER = '/tmp'
    else:
        # Em desenvolvimento, usar variável de ambiente ou padrão
        UPLOAD_FOLDER = upload_folder_env if upload_folder_env else './uploads'
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Configurações de OCR
    OCR_ENABLED = os.getenv('OCR_ENABLED', 'True').lower() == 'true'
    
    # Configurações específicas da Vercel
    @staticmethod
    def get_upload_folder():
        """Retorna a pasta de uploads correta para o ambiente"""
        if IS_VERCEL:
            # Na Vercel, usar /tmp que é o único diretório gravável
            upload_dir = '/tmp/uploads'
            os.makedirs(upload_dir, exist_ok=True)
            return upload_dir
        else:
            # Em desenvolvimento, usar pasta local
            upload_dir = Config.UPLOAD_FOLDER
            os.makedirs(upload_dir, exist_ok=True)
            return upload_dir
