import PageHeader from "../../components/page-header";

export default function ContractsPage() {
  return (
    <>
      <PageHeader title="Contracts" subtitle="Structure prête pour brancher les endpoints FastAPI" />
      <div className="card">
        <p>Cette page est scaffoldée et prête à recevoir :</p>
        <ul>
          <li>tableau de données</li>
          <li>filtres/recherche</li>
          <li>actions CRUD</li>
          <li>détails contextuels</li>
        </ul>
      </div>
      <div className="card">
        <p className="small">Prochaine étape: connecter cette page aux routes API correspondantes.</p>
      </div>
    </>
  );
}
