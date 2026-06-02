from enum import Enum


class PapelUsuario(str, Enum):
    ADM = "ADM"
    ALU = "ALU"
    CLI = "CLI"
    PRO = "PRO"


class NivelAcesso(str, Enum):
    LEI = "LEI"
    ESC = "ESC"
    ADM = "ADM"


class TipoModelo(str, Enum):
    ARM = "ARM"  # ARIMA
    RLN = "RLN"  # Regressão Linear
    ARD = "ARD"  # Árvore de Decisão
    RFO = "RFO"  # Random Forest
    RNR = "RNR"  # Rede Neural Recorrente (LSTM)


class StatusExecucao(str, Enum):
    PDT = "PDT"  # Pendente
    EAM = "EAM"  # Em Andamento
    CCD = "CCD"  # Concluído
    ERR = "ERR"  # Erro
