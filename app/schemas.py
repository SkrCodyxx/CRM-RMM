from datetime import datetime

from pydantic import BaseModel, Field

from app.models import (
    AlertSeverity,
    ContractType,
    InvoiceStatus,
    OpportunityStatus,
    ProspectStatus,
    TicketPriority,
    TicketStatus,
    TriggerType,
)


class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    legal_info: str | None = None


class ClientOut(ClientCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactCreate(BaseModel):
    client_id: int
    name: str
    email: str | None = None
    role: str | None = None


class ContactOut(ContactCreate):
    id: int

    model_config = {"from_attributes": True}


class ProspectCreate(BaseModel):
    company_name: str
    contact_name: str | None = None
    email: str | None = None
    status: ProspectStatus = ProspectStatus.LEAD


class ProspectOut(ProspectCreate):
    id: int

    model_config = {"from_attributes": True}


class OpportunityCreate(BaseModel):
    prospect_id: int
    title: str
    estimated_amount: float = 0
    status: OpportunityStatus = OpportunityStatus.OPEN


class OpportunityOut(OpportunityCreate):
    id: int

    model_config = {"from_attributes": True}


class TechnicianCreate(BaseModel):
    name: str
    email: str


class TechnicianOut(TechnicianCreate):
    id: int

    model_config = {"from_attributes": True}


class ContractCreate(BaseModel):
    client_id: int
    type: ContractType
    total_hours: float | None = None
    hourly_rate: float = 0
    monthly_price: float | None = None
    monthly_units: int | None = None


class ContractOut(BaseModel):
    id: int
    client_id: int
    type: ContractType
    total_hours: float | None = None
    remaining_hours: float | None = None
    hourly_rate: float
    monthly_price: float | None = None
    monthly_units: int | None = None

    model_config = {"from_attributes": True}


class MachineCreate(BaseModel):
    client_id: int
    hostname: str
    os_name: str
    cpu_model: str | None = None
    ram_total_gb: float | None = None
    agent_version: str | None = None


class MachineOut(MachineCreate):
    id: int
    heartbeat_at: datetime | None = None
    last_inventory_at: datetime | None = None

    model_config = {"from_attributes": True}


class HeartbeatCreate(BaseModel):
    agent_version: str | None = None


class MetricCreate(BaseModel):
    cpu_percent: float = Field(ge=0, le=100)
    ram_percent: float = Field(ge=0, le=100)
    disk_percent: float = Field(ge=0, le=100)


class MetricOut(MetricCreate):
    id: int
    machine_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertCreate(BaseModel):
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str
    details: str = ""
    auto_create_ticket: bool = False


class AlertOut(BaseModel):
    id: int
    machine_id: int
    severity: AlertSeverity
    title: str
    details: str
    ticket_id: int | None = None

    model_config = {"from_attributes": True}


class InventoryCreate(BaseModel):
    raw_json: dict


class InventoryOut(BaseModel):
    id: int
    machine_id: int
    raw_json: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketCreate(BaseModel):
    client_id: int
    machine_id: int | None = None
    technician_id: int | None = None
    contract_id: int | None = None
    priority: TicketPriority = TicketPriority.NORMAL
    description: str


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    technician_id: int | None = None
    priority: TicketPriority | None = None


class TicketOut(BaseModel):
    id: int
    client_id: int
    machine_id: int | None
    technician_id: int | None
    contract_id: int | None
    status: TicketStatus
    priority: TicketPriority
    description: str

    model_config = {"from_attributes": True}


class TimeEntryCreate(BaseModel):
    ticket_id: int
    technician_id: int
    duration_hours: float = Field(gt=0)
    billable: bool = True


class TimeEntryOut(BaseModel):
    id: int
    ticket_id: int
    technician_id: int
    duration_hours: float
    billable: bool
    validated: bool

    model_config = {"from_attributes": True}


class InterventionCreate(BaseModel):
    ticket_id: int
    technician_id: int
    starts_at: datetime
    ends_at: datetime
    remote: bool = True


class InterventionOut(InterventionCreate):
    id: int

    model_config = {"from_attributes": True}


class InvoiceCreate(BaseModel):
    client_id: int
    amount: float = Field(gt=0)
    description: str = ""


class InvoiceOut(BaseModel):
    id: int
    client_id: int
    amount: float
    description: str
    status: InvoiceStatus

    model_config = {"from_attributes": True}


class SubscriptionBillingRequest(BaseModel):
    contract_id: int


class PlaybookCreate(BaseModel):
    name: str
    os_type: str
    script: str


class PlaybookOut(PlaybookCreate):
    id: int

    model_config = {"from_attributes": True}


class PlaybookRunCreate(BaseModel):
    playbook_id: int
    machine_id: int
    trigger_type: TriggerType = TriggerType.MANUAL


class PlaybookRunOut(BaseModel):
    id: int
    playbook_id: int
    machine_id: int
    trigger_type: TriggerType
    status: str
    output_log: str

    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    clients: int
    prospects: int
    open_tickets: int
    machines: int
    alerts_24h: int
    unpaid_invoices: int
