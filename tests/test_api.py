from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app


def build_client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db: Session = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_hours_bank_decrements_and_no_invoice(tmp_path: Path):
    client = build_client(tmp_path)

    c = client.post("/clients", json={"name": "ACME", "email": "acme@example.com"}).json()
    t = client.post("/technicians", json={"name": "Alice", "email": "alice@example.com"}).json()
    contract = client.post(
        "/contracts",
        json={"client_id": c["id"], "type": "hours_bank", "total_hours": 10, "hourly_rate": 100},
    ).json()
    ticket = client.post(
        "/tickets",
        json={"client_id": c["id"], "technician_id": t["id"], "contract_id": contract["id"], "description": "Help"},
    ).json()

    r = client.post(
        "/time-entries",
        json={"ticket_id": ticket["id"], "technician_id": t["id"], "duration_hours": 2.5, "billable": True},
    )
    assert r.status_code == 200

    contract_after = client.get(f"/contracts/{contract['id']}").json()
    assert contract_after["remaining_hours"] == 7.5
    assert client.get("/invoices").json() == []


def test_time_material_generates_invoice(tmp_path: Path):
    client = build_client(tmp_path)

    c = client.post("/clients", json={"name": "Beta", "email": "beta@example.com"}).json()
    t = client.post("/technicians", json={"name": "Bob", "email": "bob@example.com"}).json()
    contract = client.post(
        "/contracts",
        json={"client_id": c["id"], "type": "time_material", "hourly_rate": 80},
    ).json()
    ticket = client.post(
        "/tickets",
        json={"client_id": c["id"], "technician_id": t["id"], "contract_id": contract["id"], "description": "Install"},
    ).json()

    r = client.post(
        "/time-entries",
        json={"ticket_id": ticket["id"], "technician_id": t["id"], "duration_hours": 1.5, "billable": True},
    )
    assert r.status_code == 200

    invoices = client.get("/invoices").json()
    assert len(invoices) == 1
    assert invoices[0]["amount"] == 120.0


def test_alert_can_create_ticket(tmp_path: Path):
    client = build_client(tmp_path)

    c = client.post("/clients", json={"name": "Gamma", "email": "gamma@example.com"}).json()
    machine = client.post("/machines", json={"client_id": c["id"], "hostname": "pc-01", "os_name": "Windows 11"}).json()

    alert = client.post(
        f"/machines/{machine['id']}/alerts",
        json={"severity": "critical", "title": "CPU > 95%", "details": "Surchauffe", "auto_create_ticket": True},
    ).json()

    assert alert["ticket_id"] is not None
    tickets = client.get("/tickets").json()
    assert len(tickets) == 1
    assert tickets[0]["priority"] == "critical"


def test_subscription_billing(tmp_path: Path):
    client = build_client(tmp_path)

    c = client.post("/clients", json={"name": "Delta", "email": "delta@example.com"}).json()
    contract = client.post(
        "/contracts",
        json={"client_id": c["id"], "type": "subscription", "monthly_price": 20, "monthly_units": 15},
    ).json()

    invoice = client.post("/billing/subscription", json={"contract_id": contract["id"]}).json()
    assert invoice["amount"] == 300


def test_dashboard_counts(tmp_path: Path):
    client = build_client(tmp_path)

    client.post("/clients", json={"name": "Count", "email": "count@example.com"})
    client.post("/prospects", json={"company_name": "Lead Corp"})
    dashboard = client.get("/dashboard").json()

    assert dashboard["clients"] == 1
    assert dashboard["prospects"] == 1
