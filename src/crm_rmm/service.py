from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import uuid4

from .models import Client, Contract, ContractType, Priority, Status, Ticket, TimeEntry


@dataclass(slots=True)
class HoursEvent:
    client_id: str
    contract_id: str
    before_hours: float
    consumed_hours: float
    after_hours: float


class CRMRMMService:
    """In-memory MVP service implementing core CRM/RMM/PSA business rules."""

    def __init__(self) -> None:
        self.clients: Dict[str, Client] = {}
        self.contracts: Dict[str, Contract] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.time_entries: Dict[str, TimeEntry] = {}
        self.hours_history: List[HoursEvent] = []
        self.notifications: List[str] = []
        self.prebilling_queue: List[str] = []

    def create_client(self, name: str, email: Optional[str] = None) -> Client:
        client = Client(id=self._id("cli"), name=name, email=email)
        self.clients[client.id] = client
        return client

    def create_contract(
        self,
        client_id: str,
        contract_type: ContractType,
        hourly_rate: float,
        total_hours: float = 0.0,
        remaining_hours: float = 0.0,
        alert_threshold_hours: float = 2.0,
    ) -> Contract:
        self._get_client(client_id)
        contract = Contract(
            id=self._id("ctr"),
            client_id=client_id,
            type=contract_type,
            hourly_rate=hourly_rate,
            total_hours=total_hours,
            remaining_hours=remaining_hours,
            alert_threshold_hours=alert_threshold_hours,
        )
        self.contracts[contract.id] = contract
        return contract

    def create_ticket(
        self,
        client_id: str,
        title: str,
        description: str,
        machine_id: Optional[str] = None,
        priority: Priority = Priority.NORMALE,
        technician_id: Optional[str] = None,
    ) -> Ticket:
        self._get_client(client_id)
        ticket = Ticket(
            id=self._id("tic"),
            client_id=client_id,
            title=title,
            description=description,
            machine_id=machine_id,
            technician_id=technician_id,
            priority=priority,
        )
        self.tickets[ticket.id] = ticket
        return ticket

    def create_ticket_from_rmm_alert(
        self,
        client_id: str,
        machine_id: str,
        alert_name: str,
        alert_details: str,
        priority: Priority = Priority.HAUTE,
    ) -> Ticket:
        return self.create_ticket(
            client_id=client_id,
            machine_id=machine_id,
            title=f"Alerte RMM: {alert_name}",
            description=alert_details,
            priority=priority,
        )

    def add_time_entry(
        self,
        ticket_id: str,
        technician_id: str,
        minutes: int,
        billable: bool = True,
    ) -> TimeEntry:
        if minutes <= 0:
            raise ValueError("minutes must be positive")
        self._get_ticket(ticket_id)
        entry = TimeEntry(
            id=self._id("tim"),
            ticket_id=ticket_id,
            technician_id=technician_id,
            minutes=minutes,
            billable=billable,
            validated=False,
        )
        self.time_entries[entry.id] = entry
        return entry

    def validate_time_entry(self, entry_id: str) -> TimeEntry:
        entry = self._get_entry(entry_id)
        if entry.validated:
            return entry

        ticket = self._get_ticket(entry.ticket_id)
        ticket.total_minutes += entry.minutes

        if entry.billable:
            ticket.billable_minutes += entry.minutes
            contract = self._active_contract_for_client(ticket.client_id)
            hours = entry.minutes / 60.0
            if contract and contract.type == ContractType.BANQUE_HEURES:
                self._consume_contract_hours(contract, hours)
            else:
                hourly_rate = contract.hourly_rate if contract else 100.0
                ticket.estimated_billable_amount += hourly_rate * hours

        entry.validated = True
        return entry

    def close_ticket(self, ticket_id: str) -> Ticket:
        ticket = self._get_ticket(ticket_id)
        ticket.status = Status.FERME

        contract = self._active_contract_for_client(ticket.client_id)
        covered_by_bank = (
            contract is not None
            and contract.type == ContractType.BANQUE_HEURES
            and ticket.billable_minutes > 0
        )
        if ticket.billable_minutes > 0 and not covered_by_bank:
            ticket.prebilling_queued = True
            self.prebilling_queue.append(ticket.id)

        return ticket

    def _consume_contract_hours(self, contract: Contract, consumed_hours: float) -> None:
        before = contract.remaining_hours
        after = max(0.0, before - consumed_hours)
        contract.remaining_hours = after
        self.hours_history.append(
            HoursEvent(
                client_id=contract.client_id,
                contract_id=contract.id,
                before_hours=before,
                consumed_hours=consumed_hours,
                after_hours=after,
            )
        )
        if after <= contract.alert_threshold_hours:
            self.notifications.append(
                f"Alerte: contrat {contract.id} du client {contract.client_id} sous seuil ({after:.2f}h restantes)."
            )

    def _active_contract_for_client(self, client_id: str) -> Optional[Contract]:
        candidates = [c for c in self.contracts.values() if c.client_id == client_id]
        return candidates[0] if candidates else None

    def _get_client(self, client_id: str) -> Client:
        if client_id not in self.clients:
            raise KeyError(f"unknown client: {client_id}")
        return self.clients[client_id]

    def _get_ticket(self, ticket_id: str) -> Ticket:
        if ticket_id not in self.tickets:
            raise KeyError(f"unknown ticket: {ticket_id}")
        return self.tickets[ticket_id]

    def _get_entry(self, entry_id: str) -> TimeEntry:
        if entry_id not in self.time_entries:
            raise KeyError(f"unknown time entry: {entry_id}")
        return self.time_entries[entry_id]

    @staticmethod
    def _id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:10]}"
