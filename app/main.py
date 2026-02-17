from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import (
    Alert,
    Client,
    Contact,
    Contract,
    ContractType,
    Intervention,
    InventorySnapshot,
    Invoice,
    Machine,
    MetricSample,
    Opportunity,
    Playbook,
    PlaybookRun,
    Prospect,
    Technician,
    Ticket,
    TimeEntry,
)
from app.schemas import (
    AlertCreate,
    AlertOut,
    ClientCreate,
    ClientOut,
    ContactCreate,
    ContactOut,
    ContractCreate,
    ContractOut,
    DashboardOut,
    HeartbeatCreate,
    InterventionCreate,
    InterventionOut,
    InventoryCreate,
    InventoryOut,
    InvoiceCreate,
    InvoiceOut,
    MachineCreate,
    MachineOut,
    MetricCreate,
    MetricOut,
    OpportunityCreate,
    OpportunityOut,
    PlaybookCreate,
    PlaybookOut,
    PlaybookRunCreate,
    PlaybookRunOut,
    ProspectCreate,
    ProspectOut,
    SubscriptionBillingRequest,
    TechnicianCreate,
    TechnicianOut,
    TicketCreate,
    TicketOut,
    TicketUpdate,
    TimeEntryCreate,
    TimeEntryOut,
)
from app.services import (
    consume_hours_bank_if_needed,
    create_ticket_from_alert,
    dashboard_counts,
    generate_invoice_from_time_entry,
    generate_subscription_invoice,
)

app = FastAPI(title="CRM-RMM-PSA API", version="0.2.0")
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/dashboard", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db)) -> dict[str, int]:
    return dashboard_counts(db)


@app.post("/clients", response_model=ClientOut)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)) -> Client:
    client = Client(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@app.get("/clients", response_model=list[ClientOut])
def list_clients(db: Session = Depends(get_db)) -> list[Client]:
    return db.query(Client).order_by(Client.created_at.desc()).all()


@app.post("/contacts", response_model=ContactOut)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)) -> Contact:
    contact = Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@app.get("/clients/{client_id}/contacts", response_model=list[ContactOut])
def list_client_contacts(client_id: int, db: Session = Depends(get_db)) -> list[Contact]:
    return db.query(Contact).filter(Contact.client_id == client_id).all()


@app.post("/prospects", response_model=ProspectOut)
def create_prospect(payload: ProspectCreate, db: Session = Depends(get_db)) -> Prospect:
    prospect = Prospect(**payload.model_dump())
    db.add(prospect)
    db.commit()
    db.refresh(prospect)
    return prospect


@app.get("/prospects", response_model=list[ProspectOut])
def list_prospects(db: Session = Depends(get_db)) -> list[Prospect]:
    return db.query(Prospect).all()


@app.post("/opportunities", response_model=OpportunityOut)
def create_opportunity(payload: OpportunityCreate, db: Session = Depends(get_db)) -> Opportunity:
    opportunity = Opportunity(**payload.model_dump())
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@app.post("/technicians", response_model=TechnicianOut)
def create_technician(payload: TechnicianCreate, db: Session = Depends(get_db)) -> Technician:
    tech = Technician(**payload.model_dump())
    db.add(tech)
    db.commit()
    db.refresh(tech)
    return tech


@app.get("/technicians", response_model=list[TechnicianOut])
def list_technicians(db: Session = Depends(get_db)) -> list[Technician]:
    return db.query(Technician).all()


@app.post("/contracts", response_model=ContractOut)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)) -> Contract:
    remaining = payload.total_hours if payload.type == ContractType.HOURS_BANK else None
    contract = Contract(**payload.model_dump(), remaining_hours=remaining)
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@app.get("/contracts/{contract_id}", response_model=ContractOut)
def get_contract(contract_id: int, db: Session = Depends(get_db)) -> Contract:
    contract = db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrat introuvable")
    return contract


@app.post("/billing/subscription", response_model=InvoiceOut)
def bill_subscription(payload: SubscriptionBillingRequest, db: Session = Depends(get_db)) -> Invoice:
    contract = db.get(Contract, payload.contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrat introuvable")
    invoice = generate_subscription_invoice(db, contract)
    db.commit()
    db.refresh(invoice)
    return invoice


@app.post("/machines", response_model=MachineOut)
def create_machine(payload: MachineCreate, db: Session = Depends(get_db)) -> Machine:
    machine = Machine(**payload.model_dump())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


@app.get("/machines", response_model=list[MachineOut])
def list_machines(db: Session = Depends(get_db)) -> list[Machine]:
    return db.query(Machine).all()


@app.post("/machines/{machine_id}/heartbeat", response_model=MachineOut)
def machine_heartbeat(machine_id: int, payload: HeartbeatCreate, db: Session = Depends(get_db)) -> Machine:
    machine = db.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine introuvable")
    machine.heartbeat_at = datetime.utcnow()
    if payload.agent_version:
        machine.agent_version = payload.agent_version
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


@app.post("/machines/{machine_id}/metrics", response_model=MetricOut)
def push_metrics(machine_id: int, payload: MetricCreate, db: Session = Depends(get_db)) -> MetricSample:
    if not db.get(Machine, machine_id):
        raise HTTPException(status_code=404, detail="Machine introuvable")
    metric = MetricSample(machine_id=machine_id, **payload.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


@app.post("/machines/{machine_id}/alerts", response_model=AlertOut)
def create_alert(machine_id: int, payload: AlertCreate, db: Session = Depends(get_db)) -> Alert:
    machine = db.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine introuvable")

    alert = Alert(machine_id=machine_id, severity=payload.severity, title=payload.title, details=payload.details)
    db.add(alert)
    db.flush()
    if payload.auto_create_ticket:
        create_ticket_from_alert(db, machine, alert)
    db.commit()
    db.refresh(alert)
    return alert


@app.post("/machines/{machine_id}/inventory", response_model=InventoryOut)
def create_inventory(machine_id: int, payload: InventoryCreate, db: Session = Depends(get_db)) -> InventorySnapshot:
    machine = db.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine introuvable")

    snapshot = InventorySnapshot(machine_id=machine_id, raw_json=payload.raw_json)
    machine.last_inventory_at = datetime.utcnow()
    db.add_all([snapshot, machine])
    db.commit()
    db.refresh(snapshot)
    return snapshot


@app.post("/tickets", response_model=TicketOut)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    ticket = Ticket(**payload.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(ticket, key, value)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()


@app.post("/time-entries", response_model=TimeEntryOut)
def create_time_entry(payload: TimeEntryCreate, db: Session = Depends(get_db)) -> TimeEntry:
    ticket = db.get(Ticket, payload.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    entry = TimeEntry(**payload.model_dump())
    db.add(entry)
    consume_hours_bank_if_needed(db, ticket, entry)
    generate_invoice_from_time_entry(db, ticket, entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.post("/interventions", response_model=InterventionOut)
def create_intervention(payload: InterventionCreate, db: Session = Depends(get_db)) -> Intervention:
    if payload.ends_at <= payload.starts_at:
        raise HTTPException(status_code=400, detail="La date de fin doit être après le début")
    intervention = Intervention(**payload.model_dump())
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


@app.get("/technicians/{technician_id}/interventions", response_model=list[InterventionOut])
def list_technician_interventions(technician_id: int, db: Session = Depends(get_db)) -> list[Intervention]:
    return db.query(Intervention).filter(Intervention.technician_id == technician_id).all()


@app.post("/invoices", response_model=InvoiceOut)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)) -> Invoice:
    invoice = Invoice(**payload.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@app.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db)) -> list[Invoice]:
    return db.query(Invoice).order_by(Invoice.created_at.desc()).all()


@app.post("/playbooks", response_model=PlaybookOut)
def create_playbook(payload: PlaybookCreate, db: Session = Depends(get_db)) -> Playbook:
    playbook = Playbook(**payload.model_dump())
    db.add(playbook)
    db.commit()
    db.refresh(playbook)
    return playbook


@app.post("/playbook-runs", response_model=PlaybookRunOut)
def run_playbook(payload: PlaybookRunCreate, db: Session = Depends(get_db)) -> PlaybookRun:
    if not db.get(Playbook, payload.playbook_id):
        raise HTTPException(status_code=404, detail="Playbook introuvable")
    if not db.get(Machine, payload.machine_id):
        raise HTTPException(status_code=404, detail="Machine introuvable")

    run = PlaybookRun(
        **payload.model_dump(),
        status="success",
        output_log="Execution simulée dans ce MVP (worker asynchrone à brancher).",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
