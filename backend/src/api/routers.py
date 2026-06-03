"""
Arquivo: routers.py
Responsabilidade: Definir as rotas REST do backend que serão consumidas pelo frontend Next.js (Grupo Alfa).
O que este arquivo faz:
- Expõe a rota GET `/api/v1/results/{modelo_treinado_id}` para retornar o resultado pré-calculado
  da predição (salvo pelo Grupo Bravo na tabela `modelo_treinado`).
- Expõe a rota POST `/api/v1/predict` que aceita o ID e retorna as predições salvaguardando retrocompatibilidade.
- A comunicação entre o front-end e esta API é livre de autenticação (JWT) conforme o alinhamento
  com a equipe de desenvolvimento.
"""
from fastapi import APIRouter, HTTPException
from src.database.db import obter_resultado_previsao

router = APIRouter()

@router.get("/api/v1/results/{modelo_treinado_id}")
async def obter_resultado_previsao_endpoint(modelo_treinado_id: str):
    """
    Retorna as previsões (JSON) de demanda pré-calculadas de um modelo treinado concluído.
    """
    resultado = await obter_resultado_previsao(modelo_treinado_id)
    if resultado is None:
        raise HTTPException(
            status_code=404, 
            detail="Resultado de previsão não encontrado ou modelo ainda em processamento/erro."
        )
    return {"status": "sucesso", "resultado": resultado}

@router.post("/api/v1/predict")
async def predict_endpoint(req: dict):
    """
    Endpoint alternativo POST para manter compatibilidade com chamadas legadas do frontend.
    Espera um corpo JSON contendo 'modelo_treinado_id'.
    """
    modelo_treinado_id = req.get("modelo_treinado_id")
    if not modelo_treinado_id:
        raise HTTPException(
            status_code=400, 
            detail="O campo 'modelo_treinado_id' é obrigatório no corpo da requisição."
        )
    
    resultado = await obter_resultado_previsao(modelo_treinado_id)
    if resultado is None:
        raise HTTPException(
            status_code=404, 
            detail="Resultado de previsão não encontrado ou modelo ainda em processamento/erro."
        )
    return {"status": "sucesso", "resultado": resultado}
