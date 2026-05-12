# Plano de Desenvolvimento - Grupo Charlie (Agente IA e Interface Telegram)

## 1. Visão Geral

Este documento define o roteiro estratégico e técnico de desenvolvimento para o **Grupo Charlie**, responsável pela construção da API REST, desenvolvimento do Agente de Inteligência Artificial utilizando o framework Agnos, e a integração com o Telegram. O objetivo principal do nosso grupo é prover a interface de comunicação inteligente com o cliente/usuário e servir as predições geradas pelo projeto **Estimador Inteligente**.

## 2. Arquitetura e Papel do Grupo Charlie

Baseado na Especificação de Requisitos e no Diagrama de Arquitetura, o Grupo Charlie gerencia os seguintes componentes vitais do "Back-end":

- **FastAPI (AI Serving API)**: Responsável por expor os endpoints de predição e inferência. O Grupo Charlie também assume a responsabilidade pela **Autenticação e Vínculo via Telegram**, garantindo que as conversas no bot sejam associadas com segurança aos usuários do sistema.
- **Agnos e LLM**: Framework utilizado para instanciar o Agente de IA, que se conecta diretamente a um modelo de linguagem (LLM). Ele será o cérebro que entende linguagem natural.
- **Interface Telegram**: Interface conversacional direta acoplada ao Agnos.
- **Carga e Processamento de Modelo**: Módulo central no nosso escopo. Tanto o FastAPI (para chamadas via Front-end) quanto o Agnos (para chamadas via Telegram) precisarão acionar este componente. Os modelos treinados (redes **LSTM**) serão armazenados pelo Grupo Bravo no Banco de Dados e nosso grupo fará a carga e inferência.

## 3. Fases de Desenvolvimento

### Fase 1: Setup, Segurança e Autenticação

- **Estruturação Docker**: Criação dos `Dockerfile` e `docker-compose.yml`. Garantir a infraestrutura para criptografia de dados em trânsito fora dos containers (HTTPS/TLS) conforme exigido no **[RNF006]**.
- **Setup de Integração**: Configurar o esqueleto do FastAPI focado em performance.
- **Autenticação Telegram (Mecanismo)**: Desenvolver a estratégia de vínculo (ex: o usuário gera um código/token no portal do Grupo Alfa e o envia para o bot no Telegram para realizar o vínculo do `chat_id`).
- **Hello World Telegram**: Registro do bot no *BotFather* do Telegram e configuração inicial.

### Fase 2: API REST e Carga do Modelo LSTM

- **Implementação do Módulo de Carga**: Criar o serviço interno em Python que se conecta ao Banco de Dados para recuperar o modelo de IA preditivo (**LSTM**) gerado pelo Grupo Bravo para um dado produto e utilizador **[RF016]**.
- **Desenvolvimento dos Endpoints FastAPI**: Criar as rotas de predição (ex: `POST /api/v1/predict`) que serão consumidas pelo Front-end quando o cliente informar a produção diária.
- **Otimização de Performance**: Garantir que a API seja extremamente ágil para responder em até 2 segundos para 95% das solicitações **[RNF001]** e suporte até 1.000 transações por minuto **[RNF002]**. O uso rigoroso de processamento assíncrono (`async def`) no FastAPI será obrigatório.

### Fase 3: Desenvolvimento do Agente IA com Agnos

- **Integração Agnos + LLM**: Configurar o framework Agnos para se comunicar com o provedor de LLM escolhido (ex: OpenAI, Llama).
- **Tool Calling (Agnos -> Modelo)**: Ensinar o Agnos a invocar o nosso módulo de "Carga e Processamento de Modelo". Se o usuário no Telegram perguntar sobre previsões, o LLM deve extrair os parâmetros da pergunta e acionar o LSTM silenciosamente.
- **Definição de Personas**: Garantir que as respostas estejam formatadas para auxiliar na tomada de decisão industrial e na redução de perdas na padaria.

### Fase 4: Integração e Autenticação Telegram

- **Conexão Telegram-Agnos**: Plugar o bot do Telegram ao Agnos. O fluxo lógico será: `Telegram -> Agnos -> LLM -> Módulo Carga LSTM -> Resposta Telegram`.
- **Implementação do Login via Telegram**: Criar o fluxo onde o Agente IA solicita a identificação do usuário no primeiro acesso, valida as credenciais contra a base do Grupo Alfa e armazena o vínculo permanente do `chat_id`.
- **Tratamento de Sessões e Privacidade**: Garantir que as predições de um usuário não sejam acessíveis por outro `chat_id`.

### Fase 5: Testes e Validação de Requisitos

- **Testes Automatizados**: Atingir a cobertura mínima de 80% de testes unitários e integração **[RNF011]**.
- **Testes de Carga**: Validar os requisitos de throughput e latência.

---

## 4. Dependências e Pontos de Contato com Outros Grupos

### Dependências com o GRUPO ALFA (Front-end)

1. **Autenticação e JWT**: Como o Grupo Alfa é Fullstack (Next.js) e responsável pelo login/auth (**[RF005]**), precisamos alinhar como o nosso FastAPI validará as sessões iniciadas por eles (ex: validação de JWT assinado pelo Next.js) para permitir o acesso aos endpoints de predição.
2. **Requisição de Predição**: O fluxo "Cliente seleciona modelo e informa produção" exige que o Next.js do Alfa envie para a nossa API o payload correto via backend-to-backend ou client-to-backend.

### Dependências com o GRUPO BRAVO (Mineração e Modelo LSTM)

1. **Armazenamento e Desserialização do Modelo**: Segundo o **[RF016]** e o diagrama, o modelo treinado (LSTM) será armazenado na "Base de Dados". O **ponto mais crítico do projeto** para nós é combinar com o Grupo Bravo **como** esse arquivo (ex: `.h5`, `.onnx` ou `.pt` do PyTorch/Keras) será lido pelo nosso "Módulo de Carga". Se eles usarem bibliotecas muito pesadas, isso impactará no tamanho da nossa imagem Docker.
2. **Filas de Treinamento**: A parte de RabbitMQ (AMQP) citada nos diagramas serve prioritariamente para avisar o Grupo Bravo que novos dados de treino chegaram **[RF015, RF017]**. Em princípio, o Grupo Charlie apenas consome os modelos prontos do banco, não entra na mensageria.

## 5. Próximos Passos (Plano de Ação Imediata)

1. **Reunião Técnica sobre o Modelo LSTM**: Agendar com o líder do Grupo Bravo para mapear a serialização do modelo no PostgreSQL e os inputs/outputs esperados para a predição.
2. **Inicialização do Projeto Charlie**: Subir o repositório Github, configurar o `docker-compose.yml` base com FastAPI e iniciar a implementação do módulo de carga de modelos, preparando a estrutura para receber tokens de autenticação do Grupo Alfa.
