const usuario = getUsuarioLogado();

const autenticado2FA =
    localStorage.getItem("autenticado_2fa");

if(autenticado2FA !== "true"){
    window.location.href =
        "verificacao-2fa.html";
}

const tipoMap = {
    ARM: "ARIMA",
    RLN: "Regressão Linear",
    ARD: "Árvore de Decisão",
    RFO: "Random Forest",
    RNR: "Rede Neural Recorrente"
};

carregarModelos();

async function carregarModelos(){

    const modelos =
        await listarModelos();

    const tbody =
        document.getElementById("listaModelos");

    tbody.innerHTML = "";

    if(modelos.length === 0){

        tbody.innerHTML = `
            <tr>
                <td colspan="4">Nenhum modelo encontrado.</td>
            </tr>
        `;

        return;
    }

    modelos.forEach(modelo => {

        const tr =
            document.createElement("tr");

        tr.innerHTML = `
            <td>${modelo.nome}</td>
            <td>${tipoMap[modelo.tipo] || modelo.tipo}</td>
            <td>${modelo.descricao || "Sem descrição"}</td>
            <td>${formatarData(modelo.criado_em)}</td>
        `;

        tbody.appendChild(tr);
    });
}

function formatarData(data){

    if(!data){
        return "-";
    }

    const partes =
        data.split("-");

    return `${partes[2]}/${partes[1]}/${partes[0]}`;
}