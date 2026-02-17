import Link from "next/link";

const links = [
  ["/dashboard", "Dashboard"],
  ["/clients", "Clients"],
  ["/prospects", "Prospects"],
  ["/contracts", "Contrats"],
  ["/tickets", "Tickets"],
  ["/interventions", "Interventions"],
  ["/invoices", "Factures"],
  ["/machines", "Machines"],
  ["/alerts", "Alertes"],
  ["/playbooks", "Playbooks"],
  ["/settings", "Paramètres"],
] as const;

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <h1>CRM-RMM-PSA</h1>
      <nav>
        {links.map(([href, label]) => (
          <Link key={href} href={href}>{label}</Link>
        ))}
      </nav>
    </aside>
  );
}
