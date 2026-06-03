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
    Realiza um SELECT real na tabela 'usuario' buscando o usuario_id, nome e papel (role).
    Retorna um dicionário com os dados do usuário ou None se não encontrado.
    """
    pool = await get_pool()
    query = """
        SELECT usuario_id AS id_cadastro, nome, papel AS role 
        FROM usuario 
        WHERE email = $1 AND senha = $2 AND ativo = TRUE AND e_delete = FALSE
    """
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, email, senha)
            if row:
                user_dict = dict(row)
                # Converte o UUID para string para ser JSON/Redis serializável
                if user_dict.get("id_cadastro"):
                    user_dict["id_cadastro"] = str(user_dict["id_cadastro"])
                return user_dict
    except Exception as e:
        print(f"Erro ao consultar credenciais do usuário: {e}")
    return None

async def listar_modelos_ativos(usuario_id: str) -> List[Dict]:
    """
    Busca os modelos (treinamentos concluídos) vinculados ao usuario_id.
    Retorna a lista de treinos concluídos com sucesso (status='CCD').
    Mapeia os campos para manter compatibilidade com a assinatura esperada pelo Agente:
    - id_modelo: UUID do modelo treinado (para identificar a estimativa específica)
    - nome_modelo: tipo do modelo/algoritmo (ex: RNR, ARM)
    - configuracao: payload de parâmetros do treino
    """
    pool = await get_pool()
    query = """
        SELECT mt.modelo_treinado_id AS id_modelo, m.tipo AS nome_modelo, mt.payload AS configuracao
        FROM modelo_treinado mt
        INNER JOIN modelo m ON mt.modelo_id = m.modelo_id
        WHERE mt.usuario_id = $1::uuid AND mt.status = 'CCD'
        ORDER BY mt.criado_em DESC
    """
    modelos = []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, usuario_id)
            for row in rows:
                modelo_dict = dict(row)
                # Garante que os campos UUID sejam convertidos em string
                if modelo_dict.get("id_modelo"):
                    modelo_dict["id_modelo"] = str(modelo_dict["id_modelo"])
                if modelo_dict.get("configuracao"):
                    try:
                        if isinstance(modelo_dict["configuracao"], str):
                            modelo_dict["configuracao"] = json.loads(modelo_dict["configuracao"])
                    except json.JSONDecodeError:
                        pass
                modelos.append(modelo_dict)
    except Exception as e:
        print(f"Erro ao consultar modelos treinados no PostgreSQL: {e}")
    return modelos

async def obter_resultado_previsao(modelo_treinado_id: str) -> Optional[dict]:
    """
    Retorna o JSON (dicionário) do resultado de previsão pré-calculado pelo Grupo Bravo
    armazenado na coluna 'resultado' da tabela 'modelo_treinado'.
    """
    pool = await get_pool()
    query = """
        SELECT resultado 
        FROM modelo_treinado 
        WHERE modelo_treinado_id = $1::uuid AND status = 'CCD'
    """
    try:
        async with pool.acquire() as conn:
            val = await conn.fetchval(query, modelo_treinado_id)
            if val:
                if isinstance(val, str):
                    return json.loads(val)
                return val
    except Exception as e:
        print(f"Erro ao buscar resultado da predição no banco: {e}")
    return None
