from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .enums import StatusExecucao, TipoModelo


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Modelo(BaseModel):
    tipo: TipoModelo
    payload_schema: dict[str, Any] = Field(default_factory=dict)
    modelo_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    criado_em: datetime = Field(default_factory=_now)
    atualizado_em: datetime = Field(default_factory=_now)

    model_config = {"from_attributes": True}


class ModeloTreinado(BaseModel):
    modelo_id: uuid.UUID
    usuario_id: uuid.UUID
    payload: dict[str, Any]
    modelo_treinado_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    status: StatusExecucao = StatusExecucao.PDT
    resultado: dict[str, Any] | None = None
    erro: str | None = None
    iniciado_em: datetime | None = None
    concluido_em: datetime | None = None
    criado_em: datetime = Field(default_factory=_now)

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def _validate_status(self) -> ModeloTreinado:
        if self.status is StatusExecucao.EAM and self.iniciado_em is None:
            raise ValueError("iniciado_em é obrigatório para status EAM")
        if self.status is StatusExecucao.CCD and self.concluido_em is None:
            raise ValueError("concluido_em é obrigatório para status CCD")
        if self.status is StatusExecucao.ERR and not self.erro:
            raise ValueError("erro é obrigatório para status ERR")
        return self
