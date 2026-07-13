# MyEduConnect — Application Web Volontairement Vulnérable

Plateforme web (fictive) reproduisant un site e-learning, **volontairement vulnérable**, construite dans le cadre d'un exercice personnel de pentest / sécurité applicative (Build → Attaque → Défense). Le projet simule une plateforme d'apprentissage en ligne ("MyEduConnect Sdn Bhd") pour servir de bac à sable réaliste : inscription/connexion, catalogue de cours, inscription aux cours, paiement simulé, gestion de profil avec upload de photo, panneau d'administration (dashboard, fiches étudiants, outil de diagnostic réseau) et une API REST.

## Sommaire

- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Structure du repo](#structure-du-repo)
- [Vulnérabilités volontairement introduites](#vulnérabilités-volontairement-introduites)
- [Installation & lancement](#installation--lancement)
- [Vérification rapide](#vérification-rapide)
- [Objectif du projet](#objectif-du-projet)
- [Avertissement légal](#avertissement-légal)

## Architecture

Architecture conteneurisée à 4 services, orchestrée avec Docker Compose sur un réseau bridge dédié (`edunet`) :

1. **Nginx** (reverse proxy) — sert les assets statiques et route les requêtes vers l'application.
2. **Flask (Python)** — application principale : auth, cours, inscriptions, paiement simulé, profils, panneau admin.
3. **PostgreSQL** — base de données (utilisateurs, cours, inscriptions, paiements, admins).
4. **API REST** (`/api/courses`, `/api/students`, `/api/ping`) — exposée par la même application Flask.

Un conteneur **SSH** additionnel est présent sur le même réseau pour les besoins d'exercices d'exploitation côté serveur/OS.

## Stack technique

| Couche | Technologie | Version |
|---|---|---|
| Serveur web | Nginx | 1.21 |
| Application | Flask (Python) | 2.3.2 (Python 3.x) |
| Base de données | PostgreSQL | 14 |
| Composant additionnel | API REST (`/api/courses`, `/api/students`, `/api/ping`) | — |
| Orchestration | Docker Compose (4 services : `db`, `app`, `nginx`, `ssh`) | — |

## Structure du repo

```
.
├── app/                     # Application Flask (code, templates, static, Dockerfile)
├── docker/ssh/               # Conteneur SSH dédié aux exercices d'exploitation OS
├── nginx/                     # Configuration Nginx (reverse proxy)
├── postgres/                  # Script d'initialisation de la base (init.sql)
├── docker-compose.yml          # Orchestration des 4 services
├── nuclei_results.txt          # Résultats de scan Nuclei
└── scan_full_platform.nmap     # Résultats de scan Nmap
```

## Vulnérabilités volontairement introduites

| # | Vulnérabilité | Catégorie | Emplacement |
|---|---|---|---|
| 1 | Injection SQL (bypass d'authentification) | CWE-89 | `POST /admin/login` |
| 2 | Injection de commandes OS (RCE) | CWE-78 | `POST /admin/network`, `GET /api/ping` |
| 3 | Upload de fichier non restreint (web shell) | CWE-434 | `POST /profile` (upload avatar) |
| 4 | Identifiants SSH faibles | CWE-521 / CWE-308 | Conteneur SSH, port 22 |
| 5 | Port PostgreSQL exposé | CWE-284 | `docker-compose.yml`, port 5432 |
| 6 | Hachage de mots de passe en MD5 non salé | CWE-916 | Tables `users` / `admins` |
| 7 | Absence de TLS — trafic HTTP et DB en clair | CWE-319 | Nginx (port 80), connexion Flask↔PostgreSQL |
| 8 | Référence directe non sécurisée (IDOR) | CWE-639 | `GET /api/students` |
| 9 | Mode debug actif / erreurs verbeuses | CWE-489 | `app.py` (`FLASK_DEBUG=1`) |
| 10 | Listing de répertoire Nginx | CWE-548 | `/static/` |
| 11 | Application exécutée en root dans le conteneur | CWE-250 | Dockerfile / `docker-compose.yml` |
| 12 | Clé secrète Flask codée en dur | CWE-798 | `app.py` (`SECRET_KEY`) |
| 13 | Données de carte bancaire partielles en clair | CWE-312 | Table `payments` |
| 14 | Utilisateur SSH dans le groupe sudo avec mot de passe réutilisé | CWE-269 | Conteneur SSH |

Le détail de chaque vulnérabilité (méthode de déclenchement, preuve de concept, correctif) est documenté dans le rapport de sécurité associé au projet (non inclus dans ce repo public).

## Installation & lancement

```bash
git clone https://github.com/chocapic78560/Application-Web-vulnerable.git
cd Application-Web-vulnerable
sudo docker-compose up --build
```

Une fois les conteneurs démarrés :

| Service | URL |
|---|---|
| Portail principal | http://localhost/ |
| Connexion admin | http://localhost/admin/login |
| API REST | http://localhost/api/courses |
| SSH | `ssh user@localhost` (port 22) |

## Vérification rapide

```bash
# Vérifier que les 4 conteneurs tournent
docker ps

# Tester l'API
curl http://localhost/api/ping
```

## Objectif du projet

Ce projet a été construit pour s'entraîner à un cycle complet de sécurité applicative :

- **Build** — concevoir une architecture réaliste et y introduire des vulnérabilités documentées (OWASP Top 10 / CWE).
- **Attaque** — reconnaissance, scan (Nmap, Nuclei, Nikto, Gobuster), exploitation manuelle (SQLi, RCE, IDOR, upload de web shell, brute-force SSH, élévation de privilèges locale).
