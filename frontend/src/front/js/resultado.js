const usuario = getUsuarioLogado();

const autenticado2FA =
    localStorage.getItem("autenticado_2fa");

if(autenticado2FA !== "true"){
    window.location.href =
        "verificacao-2fa.html";
}

const formPrevisao =
    document.getElementById("formPrevisao");

const mensagem =
    document.getElementById("mensagemResultado");

carregarUltimoResultado();

formPrevisao.addEventListener("submit", function(event){

    event.preventDefault();

    const produto =
        document.getElementById("produto").value.trim();

    const producao =
        Number(document.getElementById("producao").value);

    mensagem.innerText = "";
    mensagem.className = "form-message";

    if(!produto){
        mensagem.innerText = "Informe o produto.";
        mensagem.classList.add("error");
        return;
    }

    if(!producao || producao <= 0){
        mensagem.innerText =
            "Informe uma produção anterior válida.";

        mensagem.classList.add("error");
        return;
    }

    const previsao =
        Math.round(producao * 1.12);

    const resultado = {
        usuario_id: usuario.usuario_id,
        produto: produto,
        producao_anterior: producao,
        previsao: previsao,
        status: "CCD",
        criado_em: new Date().toISOString()
    };

    localStorage.setItem(
        "ultimo_resultado",
        JSON.stringify(resultado)
    );

    exibirResultado(resultado);

    mensagem.innerText =
        "Solicitação de previsão concluída com sucesso.";

    mensagem.classList.add("success");
});

function carregarUltimoResultado(){

    const resultadoSalvo =
        localStorage.getItem("ultimo_resultado");

    if(resultadoSalvo){
        exibirResultado(JSON.parse(resultadoSalvo));
        return;
    }

    const ultimoEnvio =
        localStorage.getItem("ultimo_envio_treino");

    if(ultimoEnvio){

        const envio =
            JSON.parse(ultimoEnvio);

        document.getElementById("produtoResultado").innerText =
            envio.produto_interesse || "Não definido";

        document.getElementById("statusResultado").innerText =
            "Pendente";
    }
}

function exibirResultado(resultado){

    document.getElementById("produtoResultado").innerText =
        resultado.produto;

    document.getElementById("producaoAnterior").innerText =
        `${resultado.producao_anterior} un.`;

    document.getElementById("previsaoIa").innerText =
        `${resultado.previsao} un.`;

    document.getElementById("statusResultado").innerText =
        traduzirStatus(resultado.status);
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

function gerarPrevisaoMock(){

    document.getElementById("produto").value =
        "Pão Francês";

    document.getElementById("producao").value =
        150;
}