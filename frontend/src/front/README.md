# Estimador Inteligente

## Sobre o Projeto

O Estimador Inteligente é uma plataforma desenvolvida para apoiar o processo de previsão de produção em padarias e pequenos negócios alimentícios.

O sistema utiliza dados históricos de produção para alimentar modelos preditivos capazes de estimar a quantidade ideal a ser produzida em períodos futuros, reduzindo desperdícios e melhorando o planejamento operacional.

---

## Objetivo

Permitir que usuários enviem dados históricos de produção, acompanhem o treinamento dos modelos e consultem previsões geradas por inteligência artificial.

---

## Funcionalidades Implementadas

### Controle de Acesso

* Login por e-mail e senha
* Verificação em duas etapas (2FA)
* Recuperação de senha

### Dashboard

* Visualização de indicadores operacionais
* Histórico de atividades
* Acompanhamento de treinamentos e previsões

### Envio de Dados

* Upload de arquivos CSV
* Upload de arquivos XLSX
* Validação de informações obrigatórias
* Preparação dos dados para processamento

### Resultados

* Solicitação de previsão
* Visualização dos resultados gerados
* Acompanhamento do status de processamento

### Modelos

* Consulta dos modelos disponíveis
* Visualização das configurações cadastradas

---

## Credenciais de Demonstração

Para fins de apresentação e validação do frontend, foram disponibilizadas credenciais simuladas.

### Acesso Administrativo

E-mail:
[admin@estimador.com](mailto:admin@estimador.com)

Senha:
123456

### Verificação em Duas Etapas (2FA)

Código:
123456

### Observação

Nesta versão acadêmica, o código 2FA é fixo e utilizado apenas para demonstração do fluxo de autenticação.

Na versão integrada, o código será gerado dinamicamente e enviado ao e-mail do utilizador por meio do serviço de autenticação.

---

## Fluxo de Autenticação

1. Informar e-mail e senha.
2. Validar credenciais.
3. Acessar a tela de verificação em duas etapas.
4. Informar o código de autenticação.
5. Acessar o sistema.

Fluxo:

Login → Verificação 2FA → Dashboard


## Arquitetura

Frontend desenvolvido para integração com os demais módulos do projeto:

Frontend (Grupo Alfa)

↓

API REST / Agente IA (Grupo Charlie)

↓

RabbitMQ

↓

Treinamento de Modelos (Grupo Bravo)

↓

Banco de Dados PostgreSQL

---

## Tecnologias Utilizadas

### Frontend

* HTML5
* CSS3
* JavaScript

### Integrações Previstas

* FastAPI
* RabbitMQ
* PostgreSQL
* Docker
* Docker Compose

---

## Estrutura do Projeto

```text
front/
│
├── index.html
├── dashboard.html
├── dados-treino.html
├── resultado.html
├── verificacao-2fa.html
├── esqueci-senha.html
├── modelos.html
│
├── css/
│   └── style.css
│
├── js/
│   ├── api.js
│   ├── login.js
│   ├── dashboard.js
│   ├── dados-treino.js
│   ├── resultado.js
│   └── modelos.js
```

## Fluxo de Utilização

1. Realizar login no sistema
2. Validar autenticação 2FA
3. Acessar o dashboard
4. Enviar dados históricos de produção
5. Solicitar previsão de produção
6. Consultar resultados gerados

---

## Equipe

### Grupo Alfa – Frontend

* Pedro Carrilho de Castro
* Paulo Vitor Avelar Rodovalho
* Matheus Henrique Silva Gonçalves
* Manuel Neto Teixeira Rodrigues
* Enzo Rodrigues Ferrari
* Adrian Enzo Souza de Oliveira

---

## Status

Projeto acadêmico desenvolvido para a disciplina de Sistemas de Informação da ESUP.
Versão atual: Protótipo funcional do frontend.
