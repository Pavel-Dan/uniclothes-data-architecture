# Cahier des charges — Architecture de donnees UNICLOTHES

## 1. Contexte

UNICLOTHES est une marque de mode parisienne (~200 collaborateurs, 30 M EUR CA, 80 000 membres UNICLUB). L'entreprise combine e-commerce, application mobile et 10 boutiques en France. Internationalisation ES/IT prevue en 2027.

Le rapport de gouvernance (Bloc 1) identifie des donnees dispersees, des doublons clients, des incoherences produit et un besoin de formalisation RGPD.

## 2. Objectifs

| Objectif | Indicateur | Statut POC |
|----------|-----------|------------|
| Vue client omnicanale | Golden record + deduplication | Implemente |
| Referentiel produit ERP | `products_golden` | Implemente |
| Entrepot analytique | Star schema `dwh` | ~2 200 ventes |
| BI consommable | Portail Streamlit (5 pages) | Implemente |
| Conformite RGPD | Export / effacement + audit | Implemente |
| Monitoring infra | Grafana + Prometheus | Implemente |
| Donnees non structurees | MinIO bucket `product-images` | Implemente |

## 3. Perimetre Phase 1

**Inclus :** client, produit, ventes, qualite data, RGPD, BI, monitoring.

**Exclus (Phase 2) :** fournisseurs, RH, catalog enterprise, MDM, cloud multi-pays.

## 4. Stack technique retenue

| Composant | Role |
|-----------|------|
| PostgreSQL 16 | raw / staging / dwh (medallion) |
| MinIO | Stockage objets (images produits) |
| Streamlit + Plotly | Portail BI custom UNICLOTHES |
| Prometheus + Grafana | Monitoring infrastructure |
| Docker Compose | Orchestration locale (ARM64) |
| Terraform | IaC declarative |

**Choix ecartes Phase 1 :** Kubernetes, Airflow, Spark, Metabase (non ARM64).

## 5. Architecture cible

```
raw → staging (golden record) → dwh (star schema)
                                    ↓
                              Streamlit BI
MinIO (objets) | Grafana/Prometheus (infra)
```

## 6. Criteres d'acceptation

- [x] `docker compose up -d --build` demarre tous les services
- [x] `run_etl.cmd` charge les donnees et construit le star schema
- [x] Streamlit affiche ventes par canal, boutiques, qualite
- [x] Grafana affiche metriques PostgreSQL
- [x] Script RGPD efface un client avec trace audit
- [x] KPI doublons mesure dans `staging.quality_metrics`

## 7. Sources simulees

| Source | Fichier seed | Volume demo |
|--------|-------------|-------------|
| CRM UNICLUB | customers_crm.csv | 480 lignes |
| E-commerce / App | customers_web.csv, orders_web.csv | 336 / 1 428 |
| POS boutiques | customers_pos.csv, orders_pos.csv | 120 / 772 |
| ERP produit | products_erp.csv | 20 references |

## 8. Regles metier

**Golden record client :** email normalise, priorite CRM > Web > POS.

**Golden record produit :** ERP = source de verite.

**Client actif 12 mois :** achat ou connexion dans les 12 derniers mois (Bloc 1).
