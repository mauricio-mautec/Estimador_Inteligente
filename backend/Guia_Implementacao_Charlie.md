# Guia Definitivo de Implementação - Grupo Charlie

Este guia detalha o "Como Fazer" técnico passo a passo para a arquitetura de responsabilidade do **Grupo Charlie** no projeto **Estimador Inteligente**. Nós usaremos FastAPI para o serviço REST, o framework **Agno** para o Agente de IA, e faremos a integração direta com o Telegram, além da carga do modelo de Machine Learning treinado.

---

## 1. Estrutura Base do Diretório `backend/`

Organização de pastas limpa e orientada a microsserviços.

```text
backend/
├── src/
│   ├── api/
│   │   ├── routers.py     # Endpoints REST (consumidos pelo Grupo Alfa Front-end)
│   │   └── auth.py        # Validação do JWT do Alfa e lógica de Vínculo Telegram
│   ├── agent/
│   │   ├── assistant.py   # Configuração do Agno (Agent) e LLM
│   │   └── tools.py       # Funções (@tool) que a IA pode invocar sozinha
│   ├── model_loader/
│   │   └── predictor.py   # Lógica para puxar o LSTM do Postgres e inferir
│   ├── database/
│   │   └── db.py          # Conexões assíncronas (asyncpg/SQLAlchemy)
│   └── main.py            # Ponto de entrada (FastAPI + AgentOS)
├── Dockerfile
├── requirements.txt
└── .env
```

---

## 2. Setup e Dependências (Fase 1)

O `requirements.txt` unirá as bibliotecas essenciais de API e de IA.

```text
fastapi
uvicorn
agno[os]              # Instala o Agno com os módulos do AgentOS e Telegram
openai                # Provider de IA para o Agno
asyncpg               # Driver PostgreSQL assíncrono (Alta performance RNF001)
pydantic
PyJWT                 # Para validar os tokens de login do Grupo Alfa
# Bibliotecas a definir em conjunto com o Grupo Bravo para o LSTM:
torch             
pandas          
```

O `Dockerfile` garante padronização:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app/src/
# Expomos a porta 8000. O Uvicorn lidará com a alta concorrência (RNF002)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3. A API REST (Fase 2)

A base do sistema é nosso FastAPI, que servirá predições para o Next.js (Grupo Alfa).

**`src/api/routers.py`**

```python
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
```

---

## 4. Carga e Processamento do Modelo LSTM (Elo com o Grupo Bravo)

O diagrama aponta que a predição acontece aqui. O Grupo Bravo treina e joga no Banco de Dados. Nós (Charlie) pegamos no Banco de Dados e executamos.

**`src/model_loader/predictor.py`**

```python
import torch
from src.database.db import get_connection

async def carregar_modelo_lstm_do_banco(user_id: int, id_produto: int):
    # Conecta no Postgres assíncrono e baixa os pesos/bytes do modelo treinado
    conn = await get_connection()
    blob_modelo = await conn.fetchval(
        "SELECT modelo_blob FROM tbl_modelos WHERE user_id = $1 AND produto_id = $2", 
        user_id, id_produto
    )
    # Lógica para converter o blob em um modelo executável de IA
    return modelo_pronto

async def fazer_predicao(user_id: int, id_produto: int, serie_temporal: list[float]) -> float:
    modelo = await carregar_modelo_lstm_do_banco(user_id, id_produto)
  
    # Processa os dados de entrada no formato esperado pelo LSTM
    tensor_entrada = torch.tensor([serie_temporal])
  
    # Executa a inferência
    predicao = modelo(tensor_entrada)
    return round(float(predicao[0]), 2)
```

---

## 5. Desenvolvimento do Agente de IA com Agno (Fase 3)

A cereja do bolo. Em vez de comandos fixos no Telegram (como `/prever`), o Agno entende conversa humana.

**`src/agent/assistant.py`**

```python
from agno.agent import Agent
from agno.tools import tool
from agno.models.openai import OpenAIChat

# Tool Calling: Ensinamos a IA a usar nossa função interna de predição
@tool
def consultar_estimativa(id_produto: int, dados_dias_anteriores: list[float]) -> str:
    """
    Use esta ferramenta SEMPRE que o gerente da padaria perguntar quanto deve produzir.
    Você extrairá o histórico das mensagens dele e usará isso para prever.
    """
    # IMPORTANTE: A função Agno pode fazer chamadas síncronas/assíncronas
    import asyncio
    from src.model_loader.predictor import fazer_predicao
    # Assume-se user_id fixado pela sessão do Agno
    previsao = asyncio.run(fazer_predicao(user_id=1, id_produto=id_produto, serie_temporal=dados_dias_anteriores))
    return f"O modelo calculou que a produção ideal hoje é de {previsao} unidades."

agente_padaria = Agent(
    name="Assistente de Gestão de Produção",
    model=OpenAIChat(id="gpt-4o"), # Ou outro LLM
    tools=[consultar_estimativa],
    description="Você é um assistente focado em ajudar padarias a evitar perdas usando nosso Estimador Inteligente LSTM.",
    enable_agentic_memory=True, # Lembra do que foi conversado
    add_history_to_context=True,
)
```

---

## 6. A "Mágica" do Vínculo Telegram e AgentOS (Fase 4)

Aqui resolvemos a questão da autenticação: conectamos o Bot do Telegram e expomos nossa API, tudo junto.

**`src/main.py`**

```python
from fastapi import FastAPI
from agno.os import AgentOS
from agno.os.interfaces.telegram import Telegram
from src.agent.assistant import agente_padaria
from src.api.routers import router
import os

# 1. Configura a Interface Telegram do Agno. Ele gerencia as sessões de chat_id nativamente.
telegram_interface = Telegram(
    agent=agente_padaria, 
    token=os.getenv("TELEGRAM_BOT_TOKEN")
)

# 2. Criação do AgentOS: o Agno encapsula o Agente e cria uma aplicação baseada em FastAPI!
agent_os = AgentOS(
    agents=[agente_padaria],
    interfaces=[telegram_interface]
)

# 3. Puxamos a aplicação FastAPI subjacente que o AgentOS criou
app = agent_os.get_app()

# 4. Injetamos as nossas rotas REST personalizadas para o Front-end (Grupo Alfa) usar
app.include_router(router)

"""
MECANISMO DE AUTENTICAÇÃO DO TELEGRAM (A desenvolver):
Para evitar que "qualquer um" converse com o bot:
1. O usuário entra no WebApp do Alfa (Next.js) e clica em "Vincular Telegram".
2. O Alfa gera um PIN "1234".
3. O usuário digita no Telegram: "vincular 1234".
4. O Agente reconhece a intenção "Vincular", checa o PIN no banco de dados e vincula
   o `chat_id` atual (que o Agno expõe no contexto da sessão) à conta Web do usuário.
"""
```

### Resumo do Fluxo Operacional:

1. **O Grupo Alfa** manda requisições para `POST /api/v1/predict` passando o token JWT deles. Nosso `auth.py` checa o JWT, e o router roda o `fazer_predicao`.
2. **O Cliente no Telegram** diz: *"Meus últimos 3 dias foram 100, 105, 110 pães. Quanto faço hoje?"*.
3. O **Agno** recebe a mensagem, entende que precisa usar a `@tool consultar_estimativa`.
4. A *tool* pega os dados, roda o mesmo `fazer_predicao` buscando o modelo do banco.
5. O **Agno** formula uma resposta simpática: *"Baseado nos dados que você me passou, o cálculo matemático ideal para hoje é de 115 pães. Bom trabalho!"*
