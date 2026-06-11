function login(){

    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value.trim();
    const erro = document.getElementById("erro");

    erro.innerText = "";

    if(!email || !senha){
        erro.innerText = "Preencha todos os campos.";
        return;
    }

    const usuario = {
        usuario_id: "9f2b6b9c-1234-4b9d-8899-000000000001",
        nome: "Victor Rodovalho",
        email: email,
        papel: "ADM",
        ativo: true,
        e_delete: false
    };

    localStorage.setItem(
        "usuario",
        JSON.stringify(usuario)
    );

    localStorage.setItem(
        "autenticado_2fa",
        "false"
    );

    window.location.href =
        "verificacao-2fa.html";
}