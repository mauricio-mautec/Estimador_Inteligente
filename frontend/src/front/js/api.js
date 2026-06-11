const API_BASE_URL = "http://localhost:8000";

const modelosMock = [
    {
        modelo_id: "mdl-001",
        nome: "Previsão Mensal de Demanda",
        tipo: "ARM",
        descricao: "Modelo ARIMA para previsão baseada em séries temporais.",
        criado_em: "2026-06-10"
    },
    {
        modelo_id: "mdl-002",
        nome: "Estimativa por Produto",
        tipo: "RFO",
        descricao: "Random Forest para estimativa baseada em histórico de produção.",
        criado_em: "2026-06-10"
    },
    {
        modelo_id: "mdl-003",
        nome: "Análise Linear de Vendas",
        tipo: "RLN",
        descricao: "Regressão Linear para análise de tendência.",
        criado_em: "2026-06-09"
    }
];

function getUsuarioLogado(){
    const usuario = localStorage.getItem("usuario");

    if(!usuario){
        window.location.href = "index.html";
        return null;
    }

    return JSON.parse(usuario);
}

function sair(){

    localStorage.removeItem("usuario");
    localStorage.removeItem("autenticado_2fa");

    window.location.href = "index.html";
}

async function listarModelos(){
    /*
    Futuro:
    const response = await fetch(`${API_BASE_URL}/modelos`);
    return await response.json();
    */

    const modelosLocais = JSON.parse(localStorage.getItem("modelos")) || [];
    return [...modelosMock, ...modelosLocais];
}

async function criarModelo(payload){
    /*
    Futuro:
    const response = await fetch(`${API_BASE_URL}/modelos`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    return await response.json();
    */

    const novoModelo = {
        modelo_id: crypto.randomUUID(),
        nome: payload.nome,
        tipo: payload.tipo,
        descricao: payload.descricao,
        payload_schema: payload.payload_schema,
        criado_em: new Date().toISOString().split("T")[0]
    };

    const modelos = JSON.parse(localStorage.getItem("modelos")) || [];
    modelos.push(novoModelo);

    localStorage.setItem("modelos", JSON.stringify(modelos));
    localStorage.setItem("ultimo_modelo", JSON.stringify(novoModelo));

    return novoModelo;
}

async function executarModelo(payload){
    /*
    Futuro:
    Enviar para FastAPI / RabbitMQ / Agente IA
    */

    const execucao = {
        execucao_id: crypto.randomUUID(),
        status: "PDT",
        mensagem: "Modelo enviado para validação do agente de IA.",
        payload
    };

    localStorage.setItem("ultima_execucao", JSON.stringify(execucao));

    return execucao;
}

async function enviarDadosTreino(payload){

    /*
    Integração futura:

    const formData = new FormData();

    formData.append("usuario_id", payload.usuario_id);
    formData.append("produto_interesse", payload.produto_interesse);
    formData.append("colunas", JSON.stringify(payload.colunas));
    formData.append("arquivo", payload.arquivo);

    const response = await fetch(`${API_BASE_URL}/treinamento/dados`, {
        method: "POST",
        body: formData
    });

    if(!response.ok){
        throw new Error("Erro ao enviar dados.");
    }

    return await response.json();
    */

    const envios =
        JSON.parse(localStorage.getItem("envios_treino")) || [];

    const envio = {
        envio_id: crypto.randomUUID(),
        ...payload,
        criado_em: new Date().toISOString()
    };

    envios.push(envio);

    localStorage.setItem(
        "envios_treino",
        JSON.stringify(envios)
    );

    localStorage.setItem(
        "ultimo_envio_treino",
        JSON.stringify(envio)
    );

    return envio;
}