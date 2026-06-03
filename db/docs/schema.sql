-- =============================================================
-- Estimador Inteligente — Schema inicial
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -------------------------------------------------------------
-- ENUMS
-- -------------------------------------------------------------

CREATE TYPE papel_usuario AS ENUM (
    'ADM',  -- Administrador
    'ALU',  -- Aluno
    'CLI',  -- Cliente
    'PRO'   -- Professor
);

CREATE TYPE nivel_acesso AS ENUM (
    'LEI',  -- Leitura
    'ESC',  -- Escrita
    'ADM'   -- Administrador
);

CREATE TYPE tipo_modelo AS ENUM (
    'ARM',  -- ARIMA
    'RLN',  -- Regressão Linear
    'ARD',  -- Árvore de Decisão
    'RFO',  -- Random Forest
    'RNR'   -- Rede Neural Recorrente (LSTM)
);

CREATE TYPE status_execucao AS ENUM (
    'PDT',  -- Pendente
    'EAM',  -- Em Andamento
    'CCD',  -- Concluído
    'ERR'   -- Erro
);

-- -------------------------------------------------------------
-- usuario
-- -------------------------------------------------------------

CREATE TABLE usuario (
    usuario_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome          VARCHAR(150)  NOT NULL,
    email         VARCHAR(254)  NOT NULL UNIQUE,
    senha         TEXT          NOT NULL,
    papel         papel_usuario NOT NULL DEFAULT 'CLI',
    ativo         BOOLEAN       NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    e_delete      BOOLEAN       NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_usuario_email ON usuario (email);

-- -------------------------------------------------------------
-- modelo
-- Catálogo dos algoritmos oferecidos pelo sistema.
-- payload_schema define os campos que o frontend deve renderizar
-- para aquele tipo de algoritmo. Gerenciado por administradores.
-- -------------------------------------------------------------

CREATE TABLE modelo (
    modelo_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome            VARCHAR(150) NOT NULL,
    tipo            tipo_modelo  NOT NULL,
    payload_schema  JSONB        NOT NULL DEFAULT '{}',
    criado_em       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_modelo_tipo ON modelo (tipo);

-- -------------------------------------------------------------
-- modelo_treinado
-- Modelo gerado: cada treino executado por um usuario.
-- payload armazena o formulário preenchido (tabela, colunas,
-- produto_treino, produto_previsao, etc.).
-- peso_path guarda o artefato treinado (.pkl / .joblib).
-- É aqui que vivem dono e histórico de execução.
-- -------------------------------------------------------------

CREATE TABLE modelo_treinado (
    modelo_treinado_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    modelo_id           UUID            NOT NULL REFERENCES modelo  (modelo_id),
    usuario_id          UUID            NOT NULL REFERENCES usuario (usuario_id),
    payload             JSONB           NOT NULL DEFAULT '{}',
    status              status_execucao NOT NULL DEFAULT 'PDT',
    resultado           JSONB, -- previsões: {"2026-02": 120.5}
    erro                TEXT,
    iniciado_em         TIMESTAMPTZ,
    concluido_em        TIMESTAMPTZ,
    criado_em           TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_treinado_modelo    ON modelo_treinado (modelo_id);
CREATE INDEX idx_treinado_usuario   ON modelo_treinado (usuario_id);
CREATE INDEX idx_treinado_status    ON modelo_treinado (status);
CREATE INDEX idx_treinado_criado_em ON modelo_treinado (criado_em DESC);

-- -------------------------------------------------------------
-- permissao_modelo_treinado
-- Controle de acesso aos modelos gerados (modelo_treinado).
-- O dono (usuario_id em modelo_treinado) tem acesso total.
-- Esta tabela concede acesso a outros usuarios.
-- -------------------------------------------------------------

CREATE TABLE permissao_modelo_treinado (
    permissao_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    modelo_treinado_id  UUID         NOT NULL REFERENCES modelo_treinado (modelo_treinado_id) ON DELETE CASCADE,
    usuario_id          UUID         NOT NULL REFERENCES usuario (usuario_id)  ON DELETE CASCADE,
    nivel               nivel_acesso NOT NULL DEFAULT 'LEI',
    criado_em           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (modelo_treinado_id, usuario_id)
);

CREATE INDEX idx_permissao_modelo_treinado_usuario ON permissao_modelo_treinado (usuario_id);
