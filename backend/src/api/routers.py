from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
# importaremos o validador de JWT que será fornecido pelo Grupo Alfa
from src.api.auth import valida_sessao_alfa 
from src.model_loader.predictor import fazer_predicao

router = APIRouter()

class SolicitacaoPrevisao(BaseModel):
    id_produto: int
    dados_serie_temporal: list[float] # A produção dos dias anteriores

@router.post("/api/v1/predict")
async def predict_endpoint(req: SolicitacaoPrevisao, current_user = Depends(valida_sessao_alfa)):
    try:
        # A API recebe os dados e manda para o processador do modelo LSTM
        # current_user.id garante que só se preveja para o usuário logado
        resultado = await fazer_predicao(current_user.id, req.id_produto, req.dados_serie_temporal)
        return {
            "status": "sucesso", 
            "produto_id": req.id_produto, 
            "previsao_hoje": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
