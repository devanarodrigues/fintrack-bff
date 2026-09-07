"""
Módulo de conexão com o banco de dados PostgreSQL
Utiliza psycopg2 para conexão direta com o banco de dados
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados PostgreSQL
    
    Returns:
        psycopg2.extensions.connection: Conexão com o banco de dados
    """
    try:
        # Usar DATABASE_URL se disponível, caso contrário usar variáveis individuais
        database_url = Config.get_database_url()
        
        if database_url and database_url.startswith('postgresql://'):
            # Usar URL completa
            connection = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
        else:
            # Usar variáveis individuais
            connection = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
        
        logger.info("Conexão com banco de dados estabelecida com sucesso")
        return connection
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        raise

def init_db():
    """
    Inicializa o banco de dados criando as tabelas necessárias
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Criar tabela de cartões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cartoes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                nome VARCHAR(100) NOT NULL,
                limite DECIMAL(10, 2),
                cor VARCHAR(7) DEFAULT '#6366f1',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Criar tabela de gastos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                gasto_pai_id UUID REFERENCES gastos(id) ON DELETE SET NULL,
                data DATE NOT NULL,
                cartao_id UUID REFERENCES cartoes(id) ON DELETE SET NULL,
                cartao_nome VARCHAR(100),
                categoria VARCHAR(100),
                descricao TEXT NOT NULL,
                valor_parcela DECIMAL(10, 2) NOT NULL,
                tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('normal', 'parcelado', 'fixo')),
                parcela_atual INTEGER DEFAULT 1,
                total_parcelas INTEGER DEFAULT 1,
                origem VARCHAR(20) NOT NULL CHECK (origem IN ('manual', 'fatura')),
                observacao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Criar índices para melhorar performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_gastos_data ON gastos(data);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_gastos_cartao ON gastos(cartao_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_gastos_gasto_pai ON gastos(gasto_pai_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_gastos_tipo ON gastos(tipo);
        """)
        
        # Inserir dados de exemplo se as tabelas estiverem vazias
        cursor.execute("SELECT COUNT(*) as count FROM cartoes")
        cartoes_count = cursor.fetchone()['count']
        
        if cartoes_count == 0:
            cursor.execute("""
                INSERT INTO cartoes (nome, limite, cor) VALUES
                ('Nubank', 5000.00, '#820ad1'),
                ('Iti', 3000.00, '#ff6b35'),
                ('Inter', 2000.00, '#ff7f00')
            """)
            logger.info("Dados de exemplo inseridos na tabela cartoes")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Banco de dados inicializado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

def execute_query(query, params=None, fetch=True):
    """
    Executa uma query SQL no banco de dados
    
    Args:
        query (str): Query SQL a ser executada
        params (tuple): Parâmetros da query
        fetch (bool): Se True, retorna os resultados da query
    
    Returns:
        list: Lista de resultados se fetch=True, None caso contrário
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        if fetch:
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        else:
            connection.commit()
            cursor.close()
            connection.close()
            return None
            
    except Exception as e:
        logger.error(f"Erro ao executar query: {e}")
        raise
