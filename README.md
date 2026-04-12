# 💀 HackBoard

Réseau social pour pentesters. Application de démonstration DevSecOps.

## Lancement en une commande

```bash
docker-compose up --build
```

Puis ouvrir http://localhost:5000

## Comptes de démo

| Username | Mot de passe | Rôle |
|----------|-------------|------|
| admin    | admin       | Fondateur |
| h4x0r    | password    | Pentester |
| newbie   | abc123      | Junior |

## Structure du projet

```
hackboard/
├── app.py              ← Application Flask
├── schema.sql          ← Structure BDD + données de démo
├── requirements.txt    ← Dépendances Python
├── Dockerfile          ← Image Docker
├── docker-compose.yml  ← Orchestration
├── templates/          ← Templates HTML Jinja2
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── writeup.html
│   ├── new_writeup.html
│   └── search.html
└── static/
    └── css/
        └── style.css
```

## Fonctionnalités

- Inscription et connexion
- Publication de write-ups CTF
- Commentaires sur les write-ups
- Recherche par titre et tags
- Profils utilisateurs

## Note pédagogique

Cette application est **volontairement vulnérable**.
Elle est conçue pour l'apprentissage du DevSecOps.
Ne pas déployer en production.
# DevSecOps_2nd_grade
