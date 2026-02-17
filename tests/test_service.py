import unittest

from src.crm_rmm.models import ContractType, Priority
from src.crm_rmm.service import CRMRMMService


class CRMRMMServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = CRMRMMService()
        self.client = self.service.create_client("ACME")

    def test_validate_time_entry_decrements_bank_hours(self) -> None:
        contract = self.service.create_contract(
            client_id=self.client.id,
            contract_type=ContractType.BANQUE_HEURES,
            hourly_rate=90.0,
            total_hours=10.0,
            remaining_hours=10.0,
            alert_threshold_hours=2.0,
        )
        ticket = self.service.create_ticket(
            client_id=self.client.id,
            title="Printer issue",
            description="Cannot print",
        )
        entry = self.service.add_time_entry(ticket.id, "tech_1", minutes=120)

        self.service.validate_time_entry(entry.id)

        self.assertEqual(contract.remaining_hours, 8.0)
        self.assertEqual(ticket.billable_minutes, 120)
        self.assertEqual(len(self.service.hours_history), 1)

    def test_contract_threshold_creates_notification(self) -> None:
        self.service.create_contract(
            client_id=self.client.id,
            contract_type=ContractType.BANQUE_HEURES,
            hourly_rate=90.0,
            total_hours=2.0,
            remaining_hours=2.0,
            alert_threshold_hours=1.5,
        )
        ticket = self.service.create_ticket(
            client_id=self.client.id,
            title="Network lag",
            description="Slow internet",
        )
        entry = self.service.add_time_entry(ticket.id, "tech_1", minutes=60)

        self.service.validate_time_entry(entry.id)

        self.assertEqual(len(self.service.notifications), 1)
        self.assertIn("sous seuil", self.service.notifications[0])

    def test_close_ticket_without_bank_hours_adds_prebilling(self) -> None:
        self.service.create_contract(
            client_id=self.client.id,
            contract_type=ContractType.TIME_MATERIAL,
            hourly_rate=120.0,
        )
        ticket = self.service.create_ticket(
            client_id=self.client.id,
            title="VPN setup",
            description="Install VPN client",
        )
        entry = self.service.add_time_entry(ticket.id, "tech_2", minutes=30)
        self.service.validate_time_entry(entry.id)

        closed = self.service.close_ticket(ticket.id)

        self.assertTrue(closed.prebilling_queued)
        self.assertIn(ticket.id, self.service.prebilling_queue)
        self.assertGreater(closed.estimated_billable_amount, 0)

    def test_create_ticket_from_rmm_alert(self) -> None:
        ticket = self.service.create_ticket_from_rmm_alert(
            client_id=self.client.id,
            machine_id="mach_1",
            alert_name="CPU High",
            alert_details="CPU > 95% for 5 minutes",
            priority=Priority.CRITIQUE,
        )

        self.assertEqual(ticket.machine_id, "mach_1")
        self.assertEqual(ticket.priority, Priority.CRITIQUE)
        self.assertTrue(ticket.title.startswith("Alerte RMM"))


if __name__ == "__main__":
    unittest.main()
