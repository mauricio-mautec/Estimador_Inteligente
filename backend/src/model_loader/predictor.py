import torch
import random
from src.database.db import get_connection

async def carregar_modelo_lstm_do_banco(user_id: int, id_produto: int):
    try:
        # Conecta no Postgres assíncrono e baixa os pesos/bytes do modelo treinado
        conn = await get_connection()
        blob_modelo = await conn.fetchval(
            "SELECT modelo_blob FROM tbl_modelos WHERE user_id = $1 AND produto_id = $2", 
            user_id, id_produto
        )
        if blob_modelo is not None:
            # Lógica para converter o blob em um modelo executável de IA (Grupo Bravo)
            # Para testes com stubs, retornamos None e usamos a predição simulada
            return None
    except Exception as e:
        print(f"Erro ao tentar carregar modelo do banco: {e}")
    return None

async def fazer_predicao(user_id: int, id_produto: int, serie_temporal: list[float]) -> float:
    modelo = await carregar_modelo_lstm_do_banco(user_id, id_produto)
  
    if modelo is None:
        # PENDÊNCIA: Quando o modelo do Grupo Bravo estiver integrado, 
        # a inferência real usará PyTorch. Por ora, simulamos uma predição inteligente.
        if not serie_temporal:
            return 0.0
        # Média simples das últimas produções mais uma variação aleatória de +/- 5%
        media = sum(serie_temporal) / len(serie_temporal)
        predicao_simulada = media * random.uniform(0.95, 1.05)
        return round(float(predicao_simulada), 2)

    try:
        # Processa os dados de entrada no formato esperado pelo LSTM
        tensor_entrada = torch.tensor([serie_temporal])
      
        # Executa a inferência
        predicao = modelo(tensor_entrada)
        return round(float(predicao[0]), 2)
    except Exception as e:
        print(f"Erro ao inferir com o modelo PyTorch: {e}. Usando fallback simulado.")
        if not serie_temporal:
            return 0.0
        media = sum(serie_temporal) / len(serie_temporal)
        return round(float(media), 2)