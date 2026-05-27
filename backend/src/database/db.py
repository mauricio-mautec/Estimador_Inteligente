"""
Arquivo: db.py
Responsabilidade: Gerenciar a conexão assíncrona com o banco de dados PostgreSQL real.
O que este arquivo faz:
- Remove o Mock antigo e estabelece uma conexão real de alta performance com o PostgreSQL utilizando `asyncpg`.
- Mantém um pool de conexões otimizado (`_pool`) que é reaproveitado durante a vida da aplicação.
- Fornece as funções `obter_usuario_por_credenciais`, `listar_modelos_ativos` e `carregar_modelo_lstm_do_banco` 
  que executam queries (SELECT) diretamente nas tabelas (`cadastro`, `modelo`, `cadastro_modelo`)
  que serão gerenciadas pelo Grupo Bravo e Alfa.
- As consultas são parametrizadas (ex: `$1`, `$2`) para prevenir ataques de SQL Injection.
"""
import os
import asyncpg
from typing import Optional, List, Dict
import json

# Variável global para armazenar o pool de conexões (Singleton pattern)
_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> asyncpg.Pool:
    """
    Inicializa e retorna o pool de conexões com o banco de dados.
    Utiliza a variável de ambiente DATABASE_URL. Remove prefixos incompatíveis nativamente com asyncpg.
    """
    global _pool
    if _pool is None:
        db_url = os.getenv("DATABASE_URL", "")
        # O asyncpg exige o prefixo 'postgresql://', por isso removemos o 'postgresql+asyncpg://' se existir
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        
        try:
            # Cria um pool que suporta de 1 a 10 conexões simultâneas
            _pool = await asyncpg.create_pool(db_url, min_size=1, max_size=10)
        except Exception as e:
            print(f"Erro Crítico: Não foi possível conectar ao banco de dados: {e}")
            raise e
    return _pool

async def obter_usuario_por_credenciais(email: str, senha: str) -> Optional[Dict]:
    """
    Busca um usuário no banco de dados validando e-mail e senha.
    Agora realiza um SELECT real na tabela 'cadastro' buscando o id, nome e role.
    Retorna um dicionário com os dados do usuário ou None se não encontrado.
    """
    pool = await get_pool()
    query = "SELECT id as id_cadastro, nome, role FROM cadastro WHERE email = $1 AND senha = $2"
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, email, senha)
            if row:
                return dict(row)
    except Exception as e:
        print(f"Erro ao consultar credenciais do usuário: {e}")
    return None

async def listar_modelos_ativos(cadastro_id: int) -> List[Dict]:
    """
    Busca os modelos ativos vinculados a um cadastro_id específico.
    Faz um INNER JOIN real entre as tabelas `modelo` e `cadastro_modelo`.
    Também verifica se a data de validade (`validade >= CURRENT_TIMESTAMP`) não expirou.
    A configuração do modelo é convertida de string JSONB para um dicionário Python.
    """
    pool = await get_pool()
    query = """
        SELECT m.id_modelo, m.nome_modelo, m.configuracao, m.arquivo_modelo 
        FROM modelo m 
        INNER JOIN cadastro_modelo cm ON m.id_modelo = cm.modelo_id 
        WHERE cm.cadastro_id = $1 AND cm.validade >= CURRENT_TIMESTAMP
    """
    modelos = []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, cadastro_id)
            for row in rows:
                modelo_dict = dict(row)
                if modelo_dict.get("configuracao"):
                    try:
                        # Se já for dict, ignora, senão converte de string JSON para dict Python
                        if isinstance(modelo_dict["configuracao"], str):
                            modelo_dict["configuracao"] = json.loads(modelo_dict["configuracao"])
                    except json.JSONDecodeError:
                        pass
                modelos.append(modelo_dict)
    except Exception as e:
        print(f"Erro ao consultar modelos ativos no PostgreSQL: {e}")
    return modelos

async def carregar_modelo_lstm_do_banco(cadastro_id: int, id_modelo: int) -> Optional[bytes]:
    """
    Retorna os bytes puros (BLOB/bytea) do arquivo `.h5` treinado pelo Grupo Bravo.
    Verifica a permissão do usuário através do INNER JOIN com a tabela `cadastro_modelo`.
    """
    pool = await get_pool()
    query = """
        SELECT m.arquivo_modelo 
        FROM modelo m 
        INNER JOIN cadastro_modelo cm ON m.id_modelo = cm.modelo_id 
        WHERE cm.cadastro_id = $1 AND m.id_modelo = $2 AND cm.validade >= CURRENT_TIMESTAMP
    """
    try:
        async with pool.acquire() as conn:
            val = await conn.fetchval(query, cadastro_id, id_modelo)
            return val
    except Exception as e:
        print(f"Erro ao buscar blob do arquivo do modelo: {e}")
    return None
