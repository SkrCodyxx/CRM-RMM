# 📘 Cahier des charges détaillé
## Plateforme CRM / RMM / PSA pour petites entreprises et MSP

## 1) Objectif du projet

Concevoir une plateforme unifiée **CRM + RMM + PSA** destinée aux petites structures (TPE/PME et MSP), avec un positionnement :

- **simple à prendre en main**,
- **rapide à déployer**,
- **économiquement accessible**,
- **suffisamment puissante** pour remplacer plusieurs outils spécialisés.

### 1.1 Objectifs métiers

- Centraliser la relation client (prospection, contrats, historique, documents).
- Industrialiser l’exploitation IT (tickets, planning, temps, interventions).
- Automatiser la facturation et le suivi de la rentabilité.
- Superviser les parcs machines avec un agent RMM et un inventaire matériel/logiciel profond.
- Réduire le temps administratif des techniciens et améliorer le niveau de service.

### 1.2 Positionnement produit

Le produit vise à concurrencer des plateformes comme NinjaOne, Atera ou Datto, avec un focus fort sur :

- la lisibilité des workflows,
- la qualité de l’automatisation,
- le coût total de possession pour petites équipes.

---

## 2) Périmètre fonctionnel

## 2.1 CRM (Customer Relationship Management)

### 2.1.1 Gestion des clients

- Fiche client complète : raison sociale, SIREN/SIRET, TVA, adresses, conditions de paiement.
- Contacts multiples par client (rôle, téléphone, email, disponibilité).
- Historique des interactions (appels, emails, notes, rendez-vous, actions commerciales).
- Gestion documentaire : contrats, devis, factures, annexes techniques.

### 2.1.2 Gestion des prospects

- Pipeline commercial paramétrable (Lead → Qualifié → Proposition → Négociation → Gagné/Perdu).
- Suivi d’opportunités avec montant, probabilité, date de clôture estimée.
- Journal d’activité commercial et rappels.
- Génération de devis/propositions depuis les opportunités.

---

## 2.2 Contrats et banque d’heures

### 2.2.1 Types de contrats

- **Banque d’heures** : packs prépayés (10h, 20h, 50h...).
- **Abonnement mensuel** : facturation par machine, utilisateur, site ou forfait.
- **Time & Material** : facturation au réel sans prépaiement.

### 2.2.2 Règles de consommation

- Décrémentation automatique des heures à la validation des temps passés.
- Distinction des temps : facturable, non-facturable, inclus contrat, hors contrat.
- Seuils d’alerte configurables (ex. 20%, 10%, 2h restantes).
- Suggestion automatique de renouvellement de pack.
- Historique complet des mouvements d’heures (audit).

---

## 2.3 Tickets & interventions (PSA)

### 2.3.1 Ticketing

- Création manuelle, par email, portail client ou automatiquement via alerte RMM.
- Statuts standards : Ouvert, En cours, En attente, Résolu, Fermé.
- Priorités : Basse, Normale, Haute, Critique.
- Assignation par technicien, équipe ou file.
- Lien natif avec client, machine, contrat et SLA.

### 2.3.2 Gestion du temps

- Saisie manuelle et minuterie start/stop.
- Validation des temps par superviseur.
- Déduction automatique sur banque d’heures selon règles contractuelles.
- Calcul de valorisation interne (coût) et externe (prix facturé).

### 2.3.3 Planification

- Agenda technicien (vue jour/semaine/mois).
- Interventions remote / sur site.
- Gestion des disponibilités, absences, charge de travail.
- Prévision de capacité équipe.

---

## 2.4 Facturation

### 2.4.1 Génération des factures

- À partir des tickets (temps hors contrat).
- À partir des abonnements récurrents.
- À partir de la vente de banques d’heures.
- Facturation périodique (mensuelle, trimestrielle, annuelle).

### 2.4.2 Cycle de vie d’une facture

- États : Brouillon → Validée → Envoyée → Payée → Relance/Impayée.
- Génération PDF (charte personnalisable).
- Envoi email avec suivi d’état.
- Historique des paiements, avoirs et relances.

### 2.4.3 Intégrations comptables (cible)

- QuickBooks
- Xero
- Sage
- Stripe (encaissement)

---

## 2.5 RMM – Monitoring et automatisation

### 2.5.1 Agent RMM (socle)

- Heartbeat agent.
- Monitoring CPU / RAM / Disque.
- Surveillance de services et processus critiques.
- Statut antivirus / EDR.
- Collecte d’événements système critiques.

### 2.5.2 Inventaire profond (“niveau atome”)

#### Matériel

- CPU : modèle, cœurs, threads, fréquence.
- RAM : slots, modules, taille, type, fréquence.
- Disques : type, capacité, série, statut SMART.
- Carte mère : modèle, firmware BIOS/UEFI.
- GPU : modèle, VRAM.
- Réseau : NIC, MAC, IP, vitesse.
- Périphériques USB critiques.

#### Logiciel

- OS : version, build, langue, date d’installation.
- Applications installées : nom, version, éditeur.
- Services : statut, type de démarrage, dépendances.
- Antivirus / EDR détecté.
- Mises à jour disponibles / en erreur.

#### Réseau

- IP, DNS, gateway.
- Appartenance domaine / AD.
- Wi-Fi SSID (si pertinent).

### 2.5.3 Fréquences de collecte

- Inventaire complet : 1 fois / jour.
- Métriques de supervision : toutes les 1 à 5 minutes.
- Alertes : quasi temps réel.

### 2.5.4 Playbooks et automatisation

- Scripts multi-OS : PowerShell, Bash, Python.
- Exécution séquentielle avec variables dynamiques.
- Déclencheurs : manuel, alerte, planning, événement système.
- Journal d’exécution complet (stdout/stderr, code retour, durée).

---

## 3) Exigences non fonctionnelles

## 3.1 Sécurité

- Authentification JWT + refresh token.
- RBAC (admin MSP, manager, technicien, client).
- Chiffrement TLS en transit et chiffrement au repos pour données sensibles.
- Journal d’audit des actions critiques.

## 3.2 Performance

- Temps de réponse API cible < 300 ms sur endpoints usuels.
- Ingestion télémétrie agent scalable par file de messages + workers.
- Pagination et filtres avancés sur vues volumineuses.

## 3.3 Disponibilité & fiabilité

- Sauvegardes planifiées, restauration testée.
- Tolerance aux pannes pour workers et jobs planifiés.
- Monitoring applicatif (métriques, logs, traces).

## 3.4 Multi-tenant

- Isolation stricte des données par tenant.
- Personnalisation branding et paramètres métiers par tenant.

---

## 4) Architecture technique cible

## 4.1 Backend

- Python **FastAPI** (ou Django REST).
- API REST versionnée.
- Auth JWT.
- Workers asynchrones : Celery / RQ / Dramatiq.

## 4.2 Frontend

- **React / Next.js**.
- Vues principales : dashboard MSP, dashboard client, tickets, interventions, facturation, parc machines.

## 4.3 Base de données

- PostgreSQL.
- Entités principales :
  - clients
  - contacts
  - opportunites
  - contrats
  - tickets
  - techniciens
  - machines
  - inventaires
  - time_entries
  - factures
  - playbooks

## 4.4 Agent

- Windows : WMI + PowerShell.
- Linux : /proc, dmidecode, lspci, lsblk.
- Communication HTTPS mutuellement authentifiée (si possible).
- Token unique par machine + rotation.

---

## 5) Modèle de données (résumé)

### 5.1 Machine

- id
- client_id
- hostname
- os_name
- cpu_model
- ram_total
- agent_version
- last_inventory_at

### 5.2 InventorySnapshot

- id
- machine_id
- created_at
- raw_json

### 5.3 Ticket

- id
- client_id
- machine_id
- technicien_id
- statut
- priorite
- description

### 5.4 TimeEntry

- id
- ticket_id
- technicien_id
- duree
- facturable

### 5.5 Contract

- id
- client_id
- type
- heures_totales
- heures_restantes
- tarif_horaire

---

## 6) Règles métier prioritaires (MVP)

1. Un temps validé sur ticket met à jour automatiquement :
   - le cumul du ticket,
   - le solde du contrat (si banque d’heures),
   - le montant potentiellement facturable.
2. Une alerte RMM peut créer automatiquement un ticket pré-rempli.
3. Un ticket clôturé non couvert par contrat alimente la file de pré-facturation.
4. Une banque d’heures sous seuil déclenche notification + proposition de renouvellement.

---

## 7) Roadmap de livraison

- **Phase 1** : CRM + Contrats + Banque d’heures.
- **Phase 2** : Tickets + Techniciens + Temps.
- **Phase 3** : Facturation.
- **Phase 4** : RMM minimal (heartbeat + métriques).
- **Phase 5** : Inventaire profond.
- **Phase 6** : Playbooks et automatisation avancée.

---

## 8) Critères d’acceptation (extraits)

- Un technicien peut créer, assigner et clôturer un ticket avec traçabilité complète.
- Le temps validé décrémente correctement le contrat associé sans écart de calcul.
- Une facture peut être générée automatiquement, exportée en PDF et marquée payée.
- L’agent remonte heartbeat + métriques + inventaire sans perte de données.
- Les données d’un tenant ne sont jamais visibles par un autre tenant.

