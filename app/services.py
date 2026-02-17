from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    Alert,
    Client,
    Contract,
    ContractType,
    Invoice,
    InvoiceStatus,
    Machine,
    Prospect,
    Ticket,
    TicketPriority,
    TicketStatus,
    TimeEntry,
)


def consume_hours_bank_if_needed(db: Session, ticket: Ticket, entry: TimeEntry) -> None:
    if not entry.billable or not ticket.contract_id:
        return

    contract = db.get(Contract, ticket.contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrat introuvable")

    if contract.type != ContractType.HOURS_BANK:
        return

    if contract.remaining_hours is None:
        raise HTTPException(status_code=400, detail="Le contrat de banque d'heures est invalide")

    contract.remaining_hours = max(0.0, contract.remaining_hours - entry.duration_hours)
    db.add(contract)


def generate_invoice_from_time_entry(db: Session, ticket: Ticket, entry: TimeEntry) -> Invoice | None:
    if not entry.billable:
        return None

    if ticket.contract_id:
        contract = db.get(Contract, ticket.contract_id)
        if contract and contract.type == ContractType.HOURS_BANK:
            return None
        hourly_rate = contract.hourly_rate if contract else 0
    else:
        hourly_rate = 120

    if hourly_rate <= 0:
        return None

    invoice = Invoice(
        client_id=ticket.client_id,
        amount=round(hourly_rate * entry.duration_hours, 2),
        description=f"Facturation automatique ticket #{ticket.id}",
    )
    db.add(invoice)
    return invoice


def generate_subscription_invoice(db: Session, contract: Contract) -> Invoice:
    if contract.type != ContractType.SUBSCRIPTION:
        raise HTTPException(status_code=400, detail="Le contrat doit être de type abonnement")

    monthly_price = contract.monthly_price or 0
    monthly_units = contract.monthly_units or 0
    amount = round(monthly_price * monthly_units, 2)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Le montant d'abonnement est invalide")

    invoice = Invoice(
        client_id=contract.client_id,
        amount=amount,
        description=f"Abonnement mensuel contrat #{contract.id}",
        status=InvoiceStatus.DRAFT,
    )
    db.add(invoice)
    return invoice


def create_ticket_from_alert(db: Session, machine: Machine, alert: Alert) -> Ticket:
    priority = TicketPriority.CRITICAL if alert.severity.value == "critical" else TicketPriority.NORMAL
    ticket = Ticket(
        client_id=machine.client_id,
        machine_id=machine.id,
        status=TicketStatus.OPEN,
        priority=priority,
        description=f"[ALERTE] {alert.title} - {alert.details}",
    )
    db.add(ticket)
    db.flush()
    alert.ticket_id = ticket.id
    db.add(alert)
    return ticket


def dashboard_counts(db: Session) -> dict[str, int]:
    last_24h = datetime.utcnow() - timedelta(hours=24)
    return {
        "clients": db.query(func.count()).select_from(Client).scalar(),
        "prospects": db.query(func.count()).select_from(Prospect).scalar(),
        "open_tickets": db.query(func.count()).select_from(Ticket).filter(
            Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.ON_HOLD])
        ).scalar(),
        "machines": db.query(func.count()).select_from(Machine).scalar(),
        "alerts_24h": db.query(func.count()).select_from(Alert).filter(Alert.created_at >= last_24h).scalar(),
        "unpaid_invoices": db.query(func.count()).select_from(Invoice).filter(Invoice.status != InvoiceStatus.PAID).scalar(),
    }
