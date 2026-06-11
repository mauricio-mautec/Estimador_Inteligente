const usuario = getUsuarioLogado();

const autenticado2FA =
    localStorage.getItem("autenticado_2fa");

if(autenticado2FA !== "true"){
    window.location.href =
        "verificacao-2fa.html";
}

const formDados =
    document.getElementById("formDadosTreino");

const inputArquivo =
    document.getElementById("arquivoTreino");

const nomeArquivo =
    document.getElementById("nomeArquivo");

const mensagem =
    document.getElementById("mensagemDados");

inputArquivo.addEventListener("change", function(){

    if(inputArquivo.files.length > 0){
        nomeArquivo.innerText =
            inputArquivo.files[0].name;
    }else{
        nomeArquivo.innerText =
            "Nenhum arquivo selecionado";
    }
});

formDados.addEventListener("submit", async function(event){

    event.preventDefault();

    mensagem.innerText = "";
    mensagem.className = "form-message";

    const arquivo = inputArquivo.files[0];

    const dados = {
        produto_interesse: getValor("produtoInteresse"),
        colunas: {
            data: getValor("colData"),
            produto: getValor("colProduto"),
            quantidade: getValor("colQuantidade")
        }
    };

    const erro = validarEnvio(arquivo, dados);

    if(erro){
        mensagem.innerText = erro;
        mensagem.classList.add("error");
        return;
    }

    const payload = {
        usuario_id: usuario.usuario_id,
        arquivo_nome: arquivo.name,
        arquivo_tipo: arquivo.type || obterExtensao(arquivo.name),
        produto_interesse: dados.produto_interesse,
        colunas: dados.colunas,
        status: "PDT",
        mensagem: "Dados enviados para a fila de treinamento."
    };

    try{
        await enviarDadosTreino(payload);

        mensagem.innerText =
            "Dados enviados com sucesso para a fila de treinamento.";

        mensagem.classList.add("success");

        setTimeout(function(){
            window.location.href = "dashboard.html";
        }, 1200);

    }catch(error){
        mensagem.innerText =
            "Erro ao enviar dados de treino.";

        mensagem.classList.add("error");
    }
});

function getValor(id){
    return document.getElementById(id).value.trim();
}

function validarEnvio(arquivo, dados){

    if(!arquivo){
        return "Selecione um arquivo CSV ou Excel.";
    }

    const nome = arquivo.name.toLowerCase();

    const formatoValido =
        nome.endsWith(".csv") ||
        nome.endsWith(".xlsx") ||
        nome.endsWith(".xls");

    if(!formatoValido){
        return "Formato inválido. Envie um arquivo .csv, .xlsx ou .xls.";
    }

    if(arquivo.size > 10 * 1024 * 1024){
        return "O arquivo deve ter no máximo 10MB.";
    }

    if(!dados.produto_interesse){
        return "Informe o produto de interesse.";
    }

    if(!dados.colunas.data){
        return "Informe a coluna de data.";
    }

    if(!dados.colunas.produto){
        return "Informe a coluna de produto.";
    }

    if(!dados.colunas.quantidade){
        return "Informe a coluna de quantidade.";
    }

    return null;
}

function obterExtensao(nomeArquivo){
    return nomeArquivo.split(".").pop();
}