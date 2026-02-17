# CRM-RMM-PSA (Backend + Front Structure)

Ce repo contient maintenant :
1. **Backend FastAPI** (CRM/RMM/PSA/facturation/playbooks)
2. **Frontend Next.js** avec **arborescence complète des pages** pour tests UI

## Arborescence principale

```text
.
├── app/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── services.py
├── frontend/
│   ├── app/
│   │   ├── dashboard/page.tsx
│   │   ├── clients/page.tsx
│   │   ├── prospects/page.tsx
│   │   ├── contracts/page.tsx
│   │   ├── tickets/page.tsx
│   │   ├── interventions/page.tsx
│   │   ├── invoices/page.tsx
│   │   ├── machines/page.tsx
│   │   ├── alerts/page.tsx
│   │   ├── playbooks/page.tsx
│   │   ├── settings/page.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── page-header.tsx
│   │   └── sidebar.tsx
│   ├── lib/mock-data.ts
│   └── package.json
└── tests/test_api.py
```

## Backend (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

UI: `http://127.0.0.1:3000`

## Pages disponibles

- Dashboard
- Clients
- Prospects
- Contrats
- Tickets
- Interventions
- Factures
- Machines
- Alertes
- Playbooks
- Paramètres

Chaque page est scaffoldée avec structure visuelle de base et prête à brancher les endpoints FastAPI.
