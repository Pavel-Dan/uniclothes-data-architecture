# Script video Loom — UNICLOTHES Data Architecture (4–5 min)

> **Avant d'enregistrer :**
> 1. `cd docker && docker compose up -d --build`
> 2. `cd ..\scripts && .\run_etl.cmd`
> 3. Ouvrir les onglets : Streamlit (8501), Grafana (3001), MinIO (9001)
> 4. Fermer notifications, agrandir fenetres

---

## INTRO — 30 sec

**Ecran :** Portail Streamlit http://localhost:8501 (logo rouge UNICLOTHES)

**Texte a dire :**

> « Bonjour. Je presente l'architecture de donnees Phase 1 d'UNICLOTHES, marque de mode omnicanale fictive. Ce projet implemente concretement mon plan de gouvernance du Bloc 1 : consolidation client et produit, conformite RGPD, et monitoring qualite. Tout est deploye localement via Docker, en open source, sur mon PC ARM64. »

---

## PARTIE 1 — Infrastructure — 40 sec

**Ecran :** Terminal PowerShell

**Actions :**
```powershell
cd docker
docker compose ps
```

**Texte a dire :**

> « Sept conteneurs tournent : PostgreSQL pour les trois couches data, Streamlit pour la BI, Grafana et Prometheus pour le monitoring, MinIO pour les images produits. Le deploiement se fait en une commande : docker compose up dash build. L'infrastructure est aussi decrite en Terraform dans le depot GitHub. »

**Montrer :** Tous les services `running` / `healthy`.

---

## PARTIE 2 — Pipeline ETL — 50 sec

**Ecran :** Terminal — resultat de `run_etl.cmd`

**Texte a dire :**

> « Quatre sources simulees alimentent la plateforme : le CRM UNICLUB, l'e-commerce et l'app, les caisses des dix boutiques, et l'ERP produit. Le script ETL charge les CSV en zone raw, applique le golden record en staging — deduplication client par email avec priorite CRM — puis construit le star schema. Resultat : environ 2 200 lignes de ventes et 560 clients unifies. »

**Montrer :** Les compteurs finaux + tableau quality_metrics (doublons en ALERT).

**Phrase cle :**

> « Le taux de doublons a 40% est volontairement en alerte : ca demontre que le monitoring qualite du Bloc 1 fonctionne. »

---

## PARTIE 3 — Portail BI Streamlit — 90 sec

**Ecran :** http://localhost:8501

**Texte a dire (page accueil) :**

> « La BI metier est un portail Streamlit custom, aux couleurs UNICLOTHES. Il est connecte directement au star schema PostgreSQL. Grafana, lui, reste reserve au monitoring infrastructure. »

**Navigation rapide :**

| Page | Montrer | Dire |
|------|---------|------|
| **Vue executive** | Courbe CA + donut canaux | « Vue direction : CA mensuel et repartition web, app, boutique. » |
| **Ventes omnicanal** | Treemap + courbe quotidienne | « Le marketing voit la performance par canal dans le temps. » |
| **Performance boutiques** | Classement horizontal | « Les dix boutiques francaises comparees par chiffre d'affaires. » |
| **Qualite & UNICLUB** | Jauge doublons rouge | « Le responsable data suit les KPIs gouvernance : doublons, consentements RGPD. » |

---

## PARTIE 4 — Monitoring Grafana — 25 sec

**Ecran :** http://localhost:3001 — login `admin` / `uniclothes_grafana`

**Texte a dire :**

> « Grafana surveille l'infrastructure : connexions PostgreSQL, taille de la base, transactions par seconde. Ce n'est pas la BI metier — c'est l'observabilite technique exigee par le cahier des charges. »

**Montrer :** Dashboard « UNICLOTHES — Data Platform Overview ».

---

## PARTIE 5 — RGPD — 30 sec

**Ecran :** Terminal

**Actions :**
```powershell
cd scripts
.\demo_rgpd.ps1
```

**Texte a dire :**

> « La conformite RGPD est implementee : droit d'acces via export_customer_gdpr, droit a l'effacement via delete_customer_gdpr, avec journal d'audit. Les analystes accedent aux donnees via une vue anonymisee sans email en clair. »

---

## PARTIE 6 — MinIO — 20 sec

**Ecran :** http://localhost:9001 — login `uniclothes_minio` / `uniclothes_minio_2026`

**Texte a dire :**

> « MinIO stocke les images produits — donnees non structurees, complementaires a PostgreSQL. Le bucket product-images est pre-configure au demarrage. »

---

## CONCLUSION — 25 sec

**Ecran :** Slide titre ou README GitHub

**Texte a dire :**

> « En resume : architecture medallion raw, staging, dwh ; star schema alimente ; BI Streamlit brandee ; monitoring Grafana ; RGPD demonstrable ; le tout reproductible via GitHub et Docker. Phase 2 : migration cloud et internationalisation ES-IT. Merci. »

---

## Checklist post-enregistrement

- [ ] Duree totale entre 4 et 5 minutes
- [ ] Streamlit montre au moins 3 pages
- [ ] Grafana montre le dashboard infra
- [ ] ETL ou compteurs mentionnes
- [ ] Lien Bloc 1 gouvernance mentionne
- [ ] GitHub URL affichee en fin

---

## Identifiants (aide-memoire)

| Service | URL | Login | Password |
|---------|-----|-------|----------|
| Streamlit | :8501 | — | — |
| Grafana | :3001 | admin | uniclothes_grafana |
| MinIO | :9001 | uniclothes_minio | uniclothes_minio_2026 |
| PostgreSQL | :5432 | uniclothes | uniclothes_dev_2026 |
