from dotenv import load_dotenv
load_dotenv()
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
1. O usuário entra no WebApp do Alfa e clica em "Vincular Telegram".
2. O Alfa gera um PIN "1234".
3. O usuário digita no Telegram: "vincular 1234".
4. O Agente reconhece a intenção "Vincular", checa o PIN no banco de dados e vincula
   o `chat_id` atual (que o Agno expõe no contexto da sessão) à conta Web do usuário.
"""