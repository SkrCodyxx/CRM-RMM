import "./globals.css";
import Sidebar from "../components/sidebar";

export const metadata = {
  title: "CRM-RMM-PSA",
  description: "Structure complète des pages front",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>
        <div className="layout">
          <Sidebar />
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
