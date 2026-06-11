const usuario = getUsuarioLogado();

const autenticado2FA =
    localStorage.getItem("autenticado_2fa");

if(autenticado2FA !== "true"){
    window.location.href =
        "verificacao-2fa.html";
}

document.getElementById("nomeUsuario").innerText = usuario.nome;

carregarDashboard();

function carregarDashboard(){

    const envios =
        JSON.parse(localStorage.getItem("envios_treino")) || [];

    const ultimoEnvio =
        JSON.parse(localStorage.getItem("ultimo_envio_treino")) || null;

    const ultimoResultado =
        JSON.parse(localStorage.getItem("ultimo_resultado")) || null;

    document.getElementById("totalEnvios").innerText =
        envios.length;

    document.getElementById("produtoMonitorado").innerText =
        ultimoEnvio?.produto_interesse || "Não definido";

    document.getElementById("statusTreinamento").innerText =
        traduzirStatus(ultimoEnvio?.status) || "Sem envio";

    document.getElementById("ultimaPrevisao").innerText =
        ultimoResultado?.previsao
            ? `${ultimoResultado.previsao} un.`
            : "Sem previsão";

    carregarTabelaAtividades(envios, ultimoResultado);
}

function carregarTabelaAtividades(envios, ultimoResultado){

    const tbody =
        document.getElementById("tabelaAtividades");

    tbody.innerHTML = "";

    const atividades = [];

    envios.forEach(envio => {
        atividades.push({
            tipo: "Envio de treino",
            produto: envio.produto_interesse,
            status: envio.status,
            data: envio.criado_em
        });
    });

    if(ultimoResultado){
        atividades.push({
            tipo: "Solicitação de previsão",
            produto: ultimoResultado.produto,
            status: ultimoResultado.status,
            data: ultimoResultado.criado_em
        });
    }

    if(atividades.length === 0){
        tbody.innerHTML = `
            <tr>
                <td colspan="4">Nenhuma atividade registrada.</td>
            </tr>
        `;
        return;
    }

    atividades
        .sort((a, b) => new Date(b.data) - new Date(a.data))
        .forEach(item => {

            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${item.tipo}</td>
                <td>${item.produto || "Não informado"}</td>
                <td>
                    <span class="status ${classeStatus(item.status)}">
                        ${traduzirStatus(item.status)}
                    </span>
                </td>
                <td>${formatarDataHora(item.data)}</td>
            `;

            tbody.appendChild(tr);
        });
}

function traduzirStatus(status){

    const mapa = {
        PDT: "Pendente",
        EAM: "Em andamento",
        CCD: "Concluído",
        ERR: "Erro"
    };

    return mapa[status] || status || "Sem status";
}

function classeStatus(status){

    const mapa = {
        PDT: "status-pending",
        EAM: "status-progress",
        CCD: "status-success",
        ERR: "status-error"
    };

    return mapa[status] || "status-pending";
}

function formatarDataHora(data){

    if(!data){
        return "---";
    }

    return new Date(data).toLocaleString("pt-BR");
}