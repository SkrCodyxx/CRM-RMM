import PageHeader from "../../components/page-header";
import { kpis, recentTickets } from "../../lib/mock-data";

export default function DashboardPage() {
  return (
    <>
      <PageHeader title="Dashboard" subtitle="Vue globale CRM + RMM + PSA" />
      <div className="grid">
        {kpis.map((k) => (
          <div key={k.label} className="card">
            <div className="small">{k.label}</div>
            <div className="kpi">{k.value}</div>
          </div>
        ))}
      </div>
      <div className="card">
        <h3>Tickets récents</h3>
        <table className="table">
          <thead><tr><th>ID</th><th>Client</th><th>Priorité</th><th>Statut</th></tr></thead>
          <tbody>
            {recentTickets.map((t) => (
              <tr key={t.id}><td>#{t.id}</td><td>{t.client}</td><td>{t.priority}</td><td>{t.status}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
