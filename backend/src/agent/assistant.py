import os
from agno.agent import Agent
from agno.tools import tool

# Configuração da LLM baseada em variáveis de ambiente
api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
model_id = os.getenv("LLM_MODEL", "gpt-4o")

if model_id.startswith("gemini"):
    from agno.models.google import Gemini
    model = Gemini(id=model_id, api_key=api_key)
else:
    from agno.models.openai import OpenAIChat
    model = OpenAIChat(id=model_id, api_key=api_key)

# Tool Calling: Ensinamos a IA a usar nossa função interna de predição
@tool
async def consultar_estimativa(id_produto: int, dados_dias_anteriores: list[float]) -> str:
    """
    Use esta ferramenta SEMPRE que o gerente da padaria perguntar quanto deve produzir.
    Você extrairá o histórico das mensagens dele e usará isso para prever.
    """
    from src.model_loader.predictor import fazer_predicao
    # Assume-se user_id fixado pela sessão do Agno
    previsao = await fazer_predicao(user_id=1, id_produto=id_produto, serie_temporal=dados_dias_anteriores)
    return f"O modelo calculou que a produção ideal hoje é de {previsao} unidades."

agente_padaria = Agent(
    name="Assistente de Gestão de Produção",
    model=model,
    tools=[consultar_estimativa],
    description="Você é um assistente focado em ajudar padarias a evitar perdas usando nosso Estimador Inteligente LSTM.",
    enable_agentic_memory=True, # Lembra do que foi conversado
    add_history_to_context=True,
)