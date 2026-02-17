export default function PageHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <h2 style={{ margin: 0 }}>{title}</h2>
      <p className="small" style={{ marginTop: 4 }}>{subtitle}</p>
    </div>
  );
}
