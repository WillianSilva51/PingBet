from enum import Enum


class MatchType(str, Enum):
    SOLO = "Solo"
    DOUBLES = "Doubles"


class MatchStatus(str, Enum):
    OPEN = "Aberta"
    SCHEDULED = "Agendada"
    FINISHED = "Finalizada"
    CANCELLED = "Cancelada"


class BetStatus(str, Enum):
    WON = "Venceu"
    LOST = "Perdeu"
    PENDING = "Pendente"
    REFUNDED = "Reembolsado"
