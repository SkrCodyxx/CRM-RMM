from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ContractType(str, Enum):
    BANQUE_HEURES = "banque_heures"
    ABONNEMENT = "abonnement"
    TIME_MATERIAL = "time_material"


class Status(str, Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    EN_ATTENTE = "en_attente"
    RESOLU = "resolu"
    FERME = "ferme"


class Priority(str, Enum):
    BASSE = "basse"
    NORMALE = "normale"
    HAUTE = "haute"
    CRITIQUE = "critique"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Client:
    id: str
    name: str
    email: Optional[str] = None


@dataclass(slots=True)
class Contract:
    id: str
    client_id: str
    type: ContractType
    hourly_rate: float
    total_hours: float = 0.0
    remaining_hours: float = 0.0
    alert_threshold_hours: float = 2.0


@dataclass(slots=True)
class Ticket:
    id: str
    client_id: str
    title: str
    description: str
    machine_id: Optional[str] = None
    technician_id: Optional[str] = None
    status: Status = Status.OUVERT
    priority: Priority = Priority.NORMALE
    created_at: datetime = field(default_factory=utcnow)
    total_minutes: int = 0
    billable_minutes: int = 0
    estimated_billable_amount: float = 0.0
    prebilling_queued: bool = False


@dataclass(slots=True)
class TimeEntry:
    id: str
    ticket_id: str
    technician_id: str
    minutes: int
    billable: bool = True
    validated: bool = False
    created_at: datetime = field(default_factory=utcnow)
