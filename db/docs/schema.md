# Schema do Banco de Dados — Estimador Inteligente

Banco: PostgreSQL 16  
Extensão: `pgcrypto` (geração de UUIDs via `gen_random_uuid()`)

---

## Enums

### `papel_usuario`
Papel do usuário no sistema.

| Valor | Descrição       |
|-------|-----------------|
| `ADM` | Administrador   |
| `ALU` | Aluno           |
| `CLI` | Cliente         |
| `PRO` | Professor       |

---

### `nivel_acesso`
Nível de permissão concedido sobre um modelo treinado.

| Valor | Descrição      |
|-------|----------------|
| `LEI` | Leitura        |
| `ESC` | Escrita        |
| `ADM` | Administrador  |

---

### `tipo_modelo`
Algoritmo de previsão utilizado.

| Valor | Algoritmo                        |
|-------|----------------------------------|
| `ARM` | ARIMA                            |
| `RLN` | Regressão Linear                 |
| `ARD` | Árvore de Decisão                |
| `RFO` | Random Forest                    |
| `RNR` | Rede Neural Recorrente (LSTM)    |

---

### `status_execucao`
Ciclo de vida de um treinamento.

| Valor | Descrição    | Transições válidas      |
|-------|--------------|-------------------------|
| `PDT` | Pendente     | → EAM                   |
| `EAM` | Em Andamento | → CCD, ERR              |
| `CCD` | Concluído    | (estado final)          |
| `ERR` | Erro         | (estado final)          |

---

## Tabelas

### `usuario`
Usuários do sistema.

| Coluna          | Tipo           | Restrições                        | Descrição                    |
|-----------------|----------------|-----------------------------------|------------------------------|
| `usuario_id`    | UUID           | PK, default `gen_random_uuid()`   | Identificador único          |
| `nome`          | VARCHAR(150)   | NOT NULL                          | Nome completo                |
| `email`         | VARCHAR(254)   | NOT NULL, UNIQUE                  | E-mail de acesso             |
| `senha`         | TEXT           | NOT NULL                          | Hash da senha                |
| `papel`         | papel_usuario  | NOT NULL, default `CLI`           | Papel do usuário             |
| `ativo`         | BOOLEAN        | NOT NULL, default `TRUE`          | Conta ativa                  |
| `criado_em`     | TIMESTAMPTZ    | NOT NULL, default `NOW()`         | Data de criação              |
| `atualizado_em` | TIMESTAMPTZ    | NOT NULL, default `NOW()`         | Última atualização           |
| `e_delete`      | BOOLEAN        | NOT NULL, default `FALSE`         | Soft delete                  |

Índices: `idx_usuario_email` em `(email)`

---

### `modelo`
Catálogo dos algoritmos disponíveis no sistema. Gerenciado por administradores.  
`payload_schema` define os campos que o frontend renderiza para cada tipo de algoritmo.

| Coluna           | Tipo        | Restrições                        | Descrição                          |
|------------------|-------------|-----------------------------------|------------------------------------|
| `modelo_id`      | UUID        | PK, default `gen_random_uuid()`   | Identificador único                |
| `tipo`           | tipo_modelo | NOT NULL, UNIQUE                  | Algoritmo (um registro por tipo)   |
| `payload_schema` | JSONB       | NOT NULL, default `{}`            | Schema do formulário do frontend   |
| `criado_em`      | TIMESTAMPTZ | NOT NULL, default `NOW()`         | Data de criação                    |
| `atualizado_em`  | TIMESTAMPTZ | NOT NULL, default `NOW()`         | Última atualização                 |

Índices: `idx_modelo_tipo` em `(tipo)`

---

### `modelo_treinado`
Instância de treinamento executada por um usuário.  
`payload` armazena os parâmetros preenchidos (tabela, colunas, produtos, etc.).  
`resultado` armazena as previsões geradas `{"2026-02": 120.5, ...}`.

| Coluna               | Tipo             | Restrições                        | Descrição                            |
|----------------------|------------------|-----------------------------------|--------------------------------------|
| `modelo_treinado_id` | UUID             | PK, default `gen_random_uuid()`   | Identificador único                  |
| `modelo_id`          | UUID             | NOT NULL, FK → `modelo`           | Algoritmo usado                      |
| `usuario_id`         | UUID             | NOT NULL, FK → `usuario`          | Dono do treinamento                  |
| `payload`            | JSONB            | NOT NULL, default `{}`            | Parâmetros do treinamento            |
| `status`             | status_execucao  | NOT NULL, default `PDT`           | Estado atual                         |
| `resultado`          | JSONB            | nullable                          | Previsões geradas                    |
| `erro`               | TEXT             | nullable                          | Mensagem de erro (status ERR)        |
| `iniciado_em`        | TIMESTAMPTZ      | nullable                          | Início do processamento              |
| `concluido_em`       | TIMESTAMPTZ      | nullable                          | Fim do processamento                 |
| `criado_em`          | TIMESTAMPTZ      | NOT NULL, default `NOW()`         | Data de criação do registro          |

Índices: `idx_treinado_modelo`, `idx_treinado_usuario`, `idx_treinado_status`, `idx_treinado_criado_em DESC`

---

### `permissao_modelo_treinado`
Controle de acesso a modelos treinados.  
O dono (`usuario_id` em `modelo_treinado`) tem acesso total implícito.  
Esta tabela concede acesso a outros usuários.

| Coluna               | Tipo         | Restrições                                        | Descrição                      |
|----------------------|--------------|---------------------------------------------------|--------------------------------|
| `permissao_id`       | UUID         | PK, default `gen_random_uuid()`                   | Identificador único            |
| `modelo_treinado_id` | UUID         | NOT NULL, FK → `modelo_treinado` ON DELETE CASCADE | Modelo compartilhado           |
| `usuario_id`         | UUID         | NOT NULL, FK → `usuario` ON DELETE CASCADE         | Usuário com acesso             |
| `nivel`              | nivel_acesso | NOT NULL, default `LEI`                           | Nível de acesso concedido      |
| `criado_em`          | TIMESTAMPTZ  | NOT NULL, default `NOW()`                         | Data da concessão              |

Restrições: UNIQUE `(modelo_treinado_id, usuario_id)` — um nível por par  
Índices: `idx_permissao_modelo_treinado_usuario` em `(usuario_id)`
