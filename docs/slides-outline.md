# Outline slides — Architecture de donnees UNICLOTHES

Ce document sert d'entree a un skill Claude de generation de slides. La presentation de l'entreprise existe deja : ne pas la recreer. Commencer directement sur l'architecture et la mise en oeuvre. Duree cible : douze a quinze minutes, suivies d'une demo live.

**Charte visuelle.** Couleur principale `#FF2D2D`, fond clair, typographie sans-serif. Un message par slide. Importer les diagrammes depuis `docs/architecture-globale.drawio`, `docs/erd-conceptuel.drawio` et `docs/star-schema.drawio`. Prevoir des captures Streamlit (vue executive et catalogue produit), Grafana et MinIO.

---

## Slide 1 — Titre

**Titre affiche :** Architecture de donnees UNICLOTHES — Phase 1

**Sous-titre :** Medallion, star schema, BI Streamlit, RGPD, MinIO

**Visuel :** Bandeau rouge avec le schema medallion (raw → staging → dwh).

**Oral :** « Cette presentation montre comment le plan de gouvernance se traduit en plateforme data deployee, avec consolidation client et produit, conformite RGPD et couverture des donnees structurees et non structurees. »

---

## Slide 2 — Problematique

**Titre affiche :** Trois enjeux adresses par l'architecture

**Contenu :** L'architecture repond aux doublons clients entre CRM, web et caisses, a la fragmentation du referentiel produit entre ERP et canaux, et a l'obligation d'operer le RGPD sur le programme UNICLUB (consentements, acces, effacement). Le schema montre trois silos actuels converger vers la Phase 1.

**Visuel :** Trois silos deconnectes avec fleche vers « Architecture Phase 1 ».

**Oral :** « Chaque composant technique correspond a un probleme identifie en gouvernance. La Phase 1 se limite a ce qui debloque la fiabilite client, produit et legale, sans sur-dimensionner l'infrastructure. »

---

## Slide 3 — Cahier des charges

**Titre affiche :** Exigences et choix retenus

**Contenu :** La vue client et produit unifiee repose sur un golden record en staging. L'analyse s'appuie sur un star schema PostgreSQL. Le RGPD est integre par design via roles, audit et anonymisation. L'observabilite se repartit entre Grafana pour l'infrastructure et Streamlit pour les KPIs metier. L'ensemble tourne en open source sous Docker, avec un seul moteur SQL.

**Visuel :** Tableau a deux colonnes (besoin / solution) ou liste numerotee en phrases courtes.

**Oral :** « Un seul PostgreSQL couvre raw, staging et dwh. Le deploiement tient en une commande Docker, ce qui correspond au contexte PME et au perimetre du projet. »

---

## Slide 4 — Architecture globale

**Titre affiche :** Architecture globale Phase 1

**Contenu :** Les CSV simules passent par `run_etl.cmd` en cinq etapes. PostgreSQL 16 structure le flux medallion. Streamlit consomme le dwh sur le port 8501. MinIO heberge les images produit ; la cle `{product_ref}.jpg` est stockee dans `dim_product.image_object_key`. Grafana et Prometheus surveillent l'infrastructure. Sept conteneurs Docker Compose forment la stack.

**Visuel :** Diagramme `docs/architecture-globale.drawio`.

**Oral :** « Le staging applique le golden record, le dwh heberge le star schema. MinIO porte les fichiers ; PostgreSQL porte la reference. Streamlit affiche le catalogue visuel a partir de cette liaison. »

---

## Slide 5 — Modele conceptuel

**Titre affiche :** Modele conceptuel Phase 1

**Contenu :** Le perimetre couvre client, produit et vente : Customer, Product, Store, Channel, Order, OrderLine et Consent pour le RGPD. Le produit est relie a un asset image (`ProductImage`) stocke dans MinIO sous la forme `{product_ref}.jpg`. Fournisseurs et RH restent hors perimetre.

**Visuel :** Diagramme `docs/erd-conceptuel.drawio`.

**Oral :** « Le modele conceptuel materialise les trois domaines prioritaires. L'extension ProductImage introduit explicitement la donnee non structuree dans le modele. »

---

## Slide 6 — Star schema

**Titre affiche :** Entrepot analytique

**Contenu :** La table de faits `fact_sales` (~2 200 lignes en demo) est entouree de cinq dimensions. `dim_product` inclut `image_object_key` et `image_url` pour le lien MinIO. La vue `dwh.v_sales_analytics` alimente Streamlit en masquant la PII pour les analystes.

**Visuel :** Diagramme `docs/star-schema.drawio`.

**Oral :** « Le star schema reste volontairement simple pour faciliter l'extension internationale. La dimension produit porte le lien vers MinIO ; la vue analytique centralise les requetes BI. »

---

## Slide 7 — Stack technique

**Titre affiche :** Stack et arbitrages

**Contenu :** PostgreSQL concentre raw, staging et dwh. Streamlit remplace Metabase, indisponible en ARM64 sur la machine de demo, et offre une BI aux couleurs de la marque. MinIO couvre les objets S3. Prometheus et Grafana assurent le monitoring. Docker Compose orchestre le POC ; Terraform formalise l'IaC. Kubernetes, Airflow et Spark sont prevus en Phase 2 si le volume le justifie.

**Visuel :** Tableau composant / role, ou icones des services.

**Oral :** « Le remplacement de Metabase par Streamlit est un arbitrage documente, lie a la contrainte materielle. Grafana ne sert pas a la BI metier : il surveille la sante de l'infrastructure. »

---

## Slide 8 — Pipeline ETL

**Titre affiche :** Flux batch et golden record

**Contenu :** `run_etl.cmd` charge les CSV en raw, unifie les sources en staging, consolide les clients par email (priorite CRM > web > POS) et les produits via l'ERP, construit le star schema, calcule les KPIs qualite et uploade les images dans MinIO. La demo produit ~560 clients golden, ~290 k EUR de CA simule et un taux de doublons d'environ 40 %, signale en alerte par le monitoring qualite.

**Visuel :** Schema des cinq etapes ou capture du terminal ETL.

**Oral :** « L'ETL s'execute en une commande. Le taux de doublons en alerte montre que le controle qualite fonctionne ; c'est un signal pour la gouvernance, pas l'absence de golden record. »

---

## Slide 9 — Portail Streamlit

**Titre affiche :** BI metier

**Contenu :** Le portail sur http://localhost:8501 propose cinq dashboards. La vue executive montre le CA mensuel et la repartition omnicanale. Les ventes omnicanal comparent les canaux web, app et boutique. La page boutiques classe les magasins. La collection affiche le catalogue visuel MinIO, les categories et les stocks. La page qualite suit les doublons, les consentements et la couverture images.

**Visuel :** Captures de la vue executive et du catalogue produit.

**Oral :** « Chaque page repond a une question metier distincte. Le catalogue visuel prouve le couplage PostgreSQL–MinIO en conditions reelles. »

---

## Slide 10 — RGPD

**Titre affiche :** Conformite by design

**Contenu :** Les roles PostgreSQL separent admin, analyst et dpo. Les analystes accedent aux donnees via `dim_customer_anonymized`. Les fonctions `audit.export_customer_gdpr` et `audit.delete_customer_gdpr` operent le droit d'acces et le droit a l'effacement. Chaque operation est tracee dans `audit.gdpr_requests`. La demo s'execute avec `scripts/demo_rgpd.ps1`.

**Visuel :** Schema roles / fonctions ou capture SQL.

**Oral :** « La conformite est integree dans la base : moindre privilege, anonymisation BI et tracabilite des demandes RGPD. »

---

## Slide 11 — Monitoring

**Titre affiche :** Observabilite infrastructure

**Contenu :** Prometheus collecte les metriques ; Grafana les visualise sur http://localhost:3001 (dashboard « Data Platform Overview »). Sont suivis les connexions PostgreSQL, la taille de la base, le debit transactionnel et l'etat des services. Les KPIs metier et qualite restent dans Streamlit.

**Visuel :** Capture du dashboard Grafana.

**Oral :** « Grafana repond a une question simple : l'infrastructure tient-elle ? Les indicateurs de doublons et de consentement relevent de la BI metier. »

---

## Slide 12 — MinIO

**Titre affiche :** Donnees non structurees

**Contenu :** Le bucket `product-images` heberge les fichiers nommes `{product_ref}.jpg`. PostgreSQL stocke la cle dans `dim_product.image_object_key`. Streamlit recupere les images via le reseau Docker (`minio:9000`). Le KPI `products_with_image_pct` mesure la couverture.

**Visuel :** Console MinIO et grille catalogue Streamlit.

**Oral :** « PostgreSQL ne stocke pas les photos : il reference les objets. MinIO heberge les fichiers. Streamlit les affiche — c'est la preuve du couplage structured / unstructured. »

---

## Slide 13 — IaC et reproductibilite

**Titre affiche :** Deploiement reproductible

**Contenu :** Le depot se structure en `docker/` (Compose), `streamlit/`, `scripts/` (SQL, seed, ETL), `terraform/` et `docs/`. La stack se lance avec `docker compose up -d --build`, les donnees avec `run_etl.cmd`. Le README documente le parcours complet.

**Visuel :** Arborescence du depot ou commandes en bloc.

**Oral :** « L'infrastructure et le pipeline sont versionnes et relancables en quelques minutes, ce qui garantit la reproductibilite du POC. »

---

## Slide 14 — Resultats et demo

**Titre affiche :** Resultats Phase 1

**Contenu :** La Phase 1 livre une architecture medallion deployee, un star schema alimente, un golden record operationnel, une BI Streamlit avec catalogue MinIO, une conformite RGPD demonstrable et un monitoring Grafana actif. La Phase 2 prevoit le cloud, un catalogue de donnees, un MDM client, du streaming et l'extension ES/IT.

**Visuel :** Tableau recapitulatif des resultats ou slide de transition vers la demo.

**Oral :** « La gouvernance et l'architecture forment un systeme coherent. Je propose maintenant une demo live sur Streamlit, MinIO, Grafana et le script RGPD. »
