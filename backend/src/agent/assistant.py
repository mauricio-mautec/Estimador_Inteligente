"""
Arquivo: assistant.py
Responsabilidade: Definir a Inteligência Artificial, sua personalidade, suas ferramentas e o fluxo conversacional no Telegram.
O que este arquivo faz:
- Configura o modelo de Linguagem (LLM) utilizando as chaves configuradas em ambiente.
- Define as "ferramentas" (funções anotadas com @tool) que a IA pode invocar por conta própria.
  As ferramentas recebem o `RunContext` do Agno, permitindo que a IA extraia o `session_id` (que é 
  o chat_id do Telegram) automaticamente, sem precisar que o modelo de linguagem adivinhe esse valor.
- Ferramentas incluídas:
  1. obter_status_usuario: Consulta o Redis via session_manager para saber se o usuário está autenticado.
  2. efetuar_login_usuario: Efetua o login usando e-mail e senha, mockando a consulta ao banco e gravando sessão.
  3. listar_modelos_do_usuario: Lista os modelos de teste associados ao usuário logado.
  4. consultar_estimativa: Simula o processamento matemático do modelo LSTM.
- As `instrucoes_bot` guiam passo a passo a IA para não cair em loops, exigindo checagem de login antes de continuar.
"""
import os
from agno.agent import Agent
from agno.tools import tool
from agno.run import RunContext
from typing import Optional, List

# Configuração da LLM baseada em variáveis de ambiente
api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
model_id = os.getenv("LLM_MODEL", "gpt-4o")

# Seleção condicional do Provider baseado no nome do modelo (ex: 'gemini-2.0-flash' carrega Google Gemini)
if model_id.startswith("gemini"):
    from agno.models.google import Gemini
    model = Gemini(id=model_id, api_key=api_key)
else:
    from agno.models.openai import OpenAIChat
    model = OpenAIChat(id=model_id, api_key=api_key)

# ── Ferramentas (Tools) da IA ──

@tool
async def obter_status_usuario(run_context: RunContext) -> str:
    """
    Verifica se o usuário atual está autenticado no sistema.
    A IA deve usar esta ferramenta no início de qualquer nova interação.
    Isso evita que a IA peça e-mail e senha de alguém que já logou.
    A ferramenta captura o `session_id` (chat_id) automaticamente pelo contexto do Agno.
    """
    from src.session.session_manager import obter_sessao
    chat_id = run_context.session_id
    sessao = await obter_sessao(chat_id)
    if sessao:
        return f"Usuário logado: {sessao['nome']} (ID: {sessao['id_cadastro']})"
    return "Usuário não está logado."

@tool
async def efetuar_login_usuario(email: str, senha: str, run_context: RunContext) -> str:
    """
    Ferramenta para autenticar o usuário. A IA chama esta função após o usuário fornecer e-mail e senha.
    Validamos as credenciais no nosso banco (neste caso, o db.py que está no formato MOCK) 
    e, se estiverem corretas, a sessão é ativada no Redis associada a este chat_id.
    Retorna uma string confirmando sucesso ou detalhando falha.
    """
    from src.database.db import obter_usuario_por_credenciais
    from src.session.session_manager import salvar_sessao
    
    email = email.strip()
    senha = str(senha).strip()
    chat_id = run_context.session_id
    
    usuario = await obter_usuario_por_credenciais(email, senha)
    if usuario:
        # Salva a sessão no Redis associando o chat_id ao id_cadastro do usuário
        sucesso = await salvar_sessao(chat_id, usuario)
        if sucesso:
            return f"Login bem-sucedido! O nome do usuário é {usuario['nome']} e o ID é {usuario['id_cadastro']}."
        else:
            return "Erro interno ao tentar salvar a sessão no cache."
    return "Credenciais inválidas. Peça para o usuário tentar novamente."

@tool
async def listar_modelos_do_usuario(run_context: RunContext) -> str:
    """
    Lista os modelos aos quais o usuário logado tem acesso.
    Garante que só liste se a sessão existir. Se existir, puxa o mock de modelos ativos (no db.py)
    e os retorna formatados para que a IA os ofereça como opções de botão no chat.
    """
    from src.session.session_manager import obter_sessao
    from src.database.db import listar_modelos_ativos
    
    chat_id = run_context.session_id
    sessao = await obter_sessao(chat_id)
    if not sessao:
        return "Erro: O usuário não está logado. Por favor, peça e-mail e senha para realizar o login."
    
    modelos = await listar_modelos_ativos(sessao['id_cadastro'])
    if not modelos:
        return "Nenhum modelo válido encontrado para este usuário."
    
    # Formata a resposta para a IA entender e repassar ao usuário
    resposta = "Modelos disponíveis:\n"
    for m in modelos:
        resposta += f"- ID: {m['id_modelo']} | Nome: {m['nome_modelo']}\n"
        resposta += f"  Parâmetros exigidos: {m.get('configuracao', 'Nenhum')}\n"
    
    return resposta

@tool
async def consultar_estimativa(id_modelo: int, parametros_preenchidos: str, run_context: RunContext) -> str:
    """
    Usa os parâmetros coletados inteligentemente pelo agente para fazer a predição real/simulada.
    Neste momento (fase de mock), repassa os dados para o predictor que executará o cálculo substituto, 
    uma vez que não há modelo treinado de verdade ainda.
    """
    from src.session.session_manager import obter_sessao
    from src.model_loader.predictor import fazer_predicao
    
    chat_id = run_context.session_id
    sessao = await obter_sessao(chat_id)
    if not sessao:
        return "Erro: O usuário não está logado."
    
    # O mock fará uma simulação simples da predição baseada nos parâmetros (dias anteriores, etc)
    return f"O modelo ID {id_modelo} processou os dados '{parametros_preenchidos}'. A predição simulada para a demanda é de 150 unidades hoje."

# ── Configuração do Agente ──

# Instruções do sistema (System Prompt). Elas ditam a personalidade e a "árvore de decisão" exata da IA
instrucoes_bot = (
    "Você é o assistente virtual do Estimador Inteligente. "
    "Sua principal função é ajudar gerentes industriais a obter previsões de produção de forma interativa.\n"
    "Siga ESTE FLUXO rigorosamente passo a passo para evitar perder contexto:\n"
    "1. No início de qualquer interação (especialmente quando o usuário disser 'Olá' ou iniciar a conversa), "
    "se você não souber se o usuário já está autenticado na sessão atual, use IMEDIATAMENTE a ferramenta 'obter_status_usuario' para checar.\n"
    "2. Se a ferramenta retornar que o usuário NÃO está logado, peça APENAS O E-MAIL do usuário. "
    "Não peça mais nada nesta etapa.\n"
    "3. Quando o usuário responder com o e-mail, peça APENAS A SENHA do usuário. Não peça mais nada.\n"
    "4. Assim que você receber a senha, use a ferramenta 'efetuar_login_usuario' passando o e-mail e a senha que o cliente informou.\n"
    "5. Se o login falhar, informe educadamente o erro ao usuário e recomece solicitando o e-mail novamente.\n"
    "6. Se o login for bem-sucedido (ou se a verificação inicial indicar que ele já logou), "
    "use imediatamente a ferramenta 'listar_modelos_do_usuario' para mostrar na tela os modelos que ele pode rodar.\n"
    "7. Quando o usuário escolher um modelo (pelo nome ou ID), analise cuidadosamente quais parâmetros são exigidos na configuração daquele modelo.\n"
    "8. Faça as perguntas para cada parâmetro exigido de maneira sequencial (uma a uma), validando o tipo (ex: int, float) "
    "antes de prosseguir para a próxima pergunta.\n"
    "9. Após receber todas as respostas de parâmetros necessárias, use a ferramenta 'consultar_estimativa' "
    "para obter a predição final e apresente esse resultado ao cliente com clareza."
)

# Configuração de persistência de memória do Agno
from agno.db.sqlite import SqliteDb

db_memoria = SqliteDb(
    db_file="telegram_memory.db",
    session_table="telegram_sessions",
    memory_table="telegram_memories"
)

# Instanciação central do Agente de IA com todas as ferramentas e regras de comportamento
agente_padaria = Agent(
    name="Assistente de Gestão de Produção",
    model=model,
    tools=[obter_status_usuario, efetuar_login_usuario, listar_modelos_do_usuario, consultar_estimativa],
    description="Você é um assistente proativo focado em ajudar indústrias e padarias a evitar perdas (desperdício) através de Modelos de IA (LSTM).",
    instructions=instrucoes_bot,
    enable_agentic_memory=True, # Garante que ele lê o histórico da conversa a cada nova mensagem
    add_history_to_context=True,
    db=db_memoria,
)