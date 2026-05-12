# Faculdade ESUP
# DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS
## Estimador Inteligente
Versão 1.0
Goiânia, 11 de Maio de 2026

|Campo|Informação|
|---|---|
|Projeto|Sistema Estimador de Produção Inteligente|
|Sistema|Estimador Inteligente|
|Versão Documento|v1|
|Data Criação|11/Maio/26|
|Última Revisão|11/Maio/26|
|Autor(es)|Prof. Maurício Junqueira|
|Aprovado por|Gildenor Cavalcanti|
|Status|Rascunho|

## HISTÓRICO DE REVISÕES

|Versão|Data|Descrição|Autor|
|--|--|--|--|
|v1.1|11/05/26|Versão inicial do documento|MJ|

## SUMÁRIO
Este documento está organizado nas seguintes seções principais:

Introdução e Visão Geral
Partes Interessadas (Stakeholders)
Escopo do Sistema
Requisitos Funcionais
Requisitos Não-Funcionais
Regras de Negócio
Restrições e Dependências
Glossário
Referências

## INTRODUÇÃO E VISÃO GERAL

### Objetivo do Documento
Este Documento de Especificação de Requisitos (ERS) descreve de forma completa e estruturada todos os requisitos funcionais e não-funcionais do sistema Estimador Inteligente. Ele serve como contrato entre a equipe de desenvolvimento (Graduandos de SI), os clientes (Empresas Participantes) e Professores de SI ESUP, garantindo alinhamento sobre o escopo, as funcionalidades esperadas e as restrições do sistema.

### Público-Alvo
- Graduando de Sistemas de Informação ESUP
- Empresas participantes
- Professores de Sistemas de Informação ESUP
- Auditores e avaliadores externos

### Convenções e Definições
- [RF-XXX] – Identificador de Requisito Funcional
- [RNF-XXX] – Identificador de Requisito Não-Funcional
- [RN-XXX] – Identificador de Regra de Negócio
- Prioridade: Alta / Média / Baixa

## Partes Interessadas (Stakeholders)

|Parte Interessada|Papel|Interesse/Expectativa|
|---|---|---|
|Graduandos de Sistemas de Informação|Desenvolvedores|Aprendizado de técnicas efetivas em processos industriais|
|Empresas Participantes|Utilizador|Acesso a tecnologias de ponta a baixo custo|
|Professor Sistemas de Informação ESUP|Fomento da capacitação dos graduandos em tecnologias emergentes|
|Faculdade ESUP|Fomento|Aproximação Indústria/Faculdade para desenvolvimento de novas parcerias|

## Escopo do Sistema
### Visão Geral
O sistema tem por finalidade treinar modelos de IA para predição de produção industrial para a melhor desempenho da atividade.

### Limites do Sistema
O sistema Estimador Inteligente inclui:
- Serviço frontend para interface responsiva
- Serviço de mineração de dados e treino de modelo de IA
- Serviço Agente de IA para utilização dos modelos e interface Telegram

O sistema NÃO incluí (fora do escopo inicialmente):
- treinamento de modelo para mais de um produto por utilizador
- comunicação via outro comunicador que não seja o Telegram

## Requisitos Funcionais

|ID|Descrição|Prioridade|
|RF-001|O sistema deve permitir que o utilizador realize login utilizando e-mail e senha|Alta|
|RF-002|O sistema deve suportar autenticação de dois fatores (2FA) via e-mail cadastrado|Alta|
|RF-003|O sistema deve exibir menagem de erro clara após três tentativas de login mal sucedidas e bloquear a conta temporariamente.|Média|
|RF-004|O sistema deve permitir recuperação de senha por e-mail|Alta|
|RF-005|O administrador deve suportar 3 perfis de acesso a saber: administrador, operador e utilizador|Alta|
|RF-006|O perfil administrador deve poder cadastrar, editar e excluir contas de usuário|Alta|
|RF-007|O perfil administrador deve poder apenas visualizar todos artefatos que compõe o sistema, incluindo os logs de operação, mas não poderá alterá-los, exceto com relação às contas de usuário.|Alta|
|RF-008|O perfil operador deve poder excluir modelos, alterar parâmetros de execução e quaisquer outros artefatos que afetem a operação do sistema, exceto acesso aos logs de operação.|Alta|
|RF-009|O perfil utilizador se limitará ao uso do modelo de predição e atualização de dados para treino de modelo.|Alta|
|RF-010|O sistema deve registar log de todas as ações realizadas para fins de auditoria.|Alta|
|RF-011|O sistema deve gerar relatório de acesso filtrados por data, usuário e tipo de operação.|Alta|
|RF-012|O sistema frontend deverá registrar os produtos de interesse de cada utilizador no banco de dados do sistema.|Alta|
|RF-013|O sistema frontend deverá receber e armazenar os dados de treino de um utilizador no banco de dados do sistema.|Alta|
|RF-014|O sistema armazenará apenas um conjunto de dados de treino por utilizador (o último enviado) onde os dados serão sempre referentes a diversos produtos.|Média|
|RF-015|Após o armazenamento de um novo conjunto de dados para um utilizador, o frontend deverá informar o serviço de treinamento de modelo, via messageria.|Alta|
|RF-016|O serviço de mineração de dados e treino de modelos deverá treinar um modelo por produto/utilizador e armazenar o resultado do treino no banco de dados do sistema.|Alta|
|RF-017|O serviço de mineração de dados e treino de modelos deverá aguardar pelo id do utlizador em uma fila de messageria.|Alta|

## Requisitos Não-Funcionais

|ID|Descrição|Prioridade|
|--|--|--|
|RNF-001|O sistema deve responder a requisições de consulta em até 2 segundos para 95% das solicitações.|Alta|
|RNF-002|O sistema deve ser capaz de processar pelo menos 1.000 transações por minuto.|Alta|
|RNF-003|O sistema deve estar disponível 99,5% do tempo (uptime), excetuando janelas de manutenção programada.|Alta|
|RNF-004|O serviço de mineração e treino de modelos deverá operar em regime de alta disponibilidade.|Alta|
|RNF-005|Backups automáticos do banco de dados devem ser realizados diariamente com retenção mínima de 30 dias e transmitidos para outra localidade.|Alta|
|RNF-006|Todos os dados em trânsito fora da composição dos containers de um serviço devem ser criptografados|Alta|
|RNF-007|O sistema deve estar em conformidade com a Lei Geral de Proteção de Dados (LGPD – Lei 13.709/2018)|Alta|
|RNF-008|O sistema deve implementar proteção contra ataques CSRF, XSS e SQL Injection.|Alta|
|RNF-009|A interface deve ser responsiva, adaptando-se a dispositivos móveis, tablets e desktops.|Alta|
|RNF-010|O tempo de aprendizado para usuários novos deve ser de até 2 horas com o material de treinamento fornecido.|Alta|
|RNF-011|O sistema deve possuir cobertura mínima de 80% de testes automatizados (unitários e integração).|Alta|
|RNF-012|O sistema deve ser compatível com os principais navegadores modernos: Chrome, Firefox, Edge e Safari.|Média|
