"""
Arquivo: session_manager.py
Responsabilidade: Gerenciar sessões temporárias dos usuários no Telegram usando Redis.
O que este arquivo faz:
- Conecta-se ao banco de cache Redis de forma assíncrona.
- Fornece funções para Salvar, Obter e Limpar sessões.
- Cada sessão vincula o chat_id (ID da conversa no Telegram) aos dados do usuário autenticado.
- Isso permite que o bot "lembre" quem está logado durante o fluxo da conversa, 
  mesmo sem acessar um banco de dados relacional principal.
"""
import os
import json
import redis.asyncio as redis
from typing import Optional, Dict

# URL de conexão com o Redis. Usa a variável de ambiente se existir, caso contrário o padrão do docker-compose
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Instância global do cliente Redis para ser reaproveitada
_redis_client: Optional[redis.Redis] = None

def get_redis() -> redis.Redis:
    """
    Inicializa (se necessário) e retorna a instância global do cliente Redis.
    Isso evita criar múltiplas conexões desnecessárias.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client

async def salvar_sessao(chat_id: str, user_data: Dict) -> bool:
    """
    Salva os dados do usuário autenticado no Redis, usando o chat_id como chave de identificação.
    A sessão expira automaticamente em 24 horas (86400 segundos) para manter o cache limpo.
    Retorna True se for salvo com sucesso.
    """
    client = get_redis()
    key = f"telegram_session:{chat_id}"
    try:
        await client.set(key, json.dumps(user_data), ex=86400)
        return True
    except Exception as e:
        print(f"Erro ao salvar sessão no Redis: {e}")
        return False

async def obter_sessao(chat_id: str) -> Optional[Dict]:
    """
    Recupera os dados da sessão do usuário no Redis a partir do chat_id fornecido pelo Telegram.
    A IA utiliza esta função para saber instantaneamente quem é o usuário com que ela está falando.
    Retorna o dicionário com os dados se encontrado, ou None se não houver sessão ativa.
    """
    client = get_redis()
    key = f"telegram_session:{chat_id}"
    try:
        data_str = await client.get(key)
        if data_str:
            return json.loads(data_str)
    except Exception as e:
        print(f"Erro ao obter sessão no Redis: {e}")
    return None

async def limpar_sessao(chat_id: str) -> bool:
    """
    Remove a sessão ativa do usuário (funciona como um Logout).
    Se o usuário desejar trocar de conta, esta função limpa a memória no Redis.
    """
    client = get_redis()
    key = f"telegram_session:{chat_id}"
    try:
        await client.delete(key)
        return True
    except Exception as e:
        print(f"Erro ao limpar sessão no Redis: {e}")
        return False
