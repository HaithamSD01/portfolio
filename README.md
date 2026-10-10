# Portfolio — Haitham Dhaimi

Site : **https://haithamdhaimiportfolio.netlify.app** · [English](https://haithamdhaimiportfolio.netlify.app/en/) · [العربية](https://haithamdhaimiportfolio.netlify.app/ar/)

Élève ingénieur en ingénierie digitale et IA en santé à SUPTECH-SANTÉ (Mohammedia). Ce dépôt contient le code de mon portfolio : deux stages présentés comme des études de cas, mes projets, mon parcours et mes formations.

## Pourquoi un site statique

Un portfolio doit charger vite, rester lisible sur un vieux téléphone et ne rien collecter sur ses visiteurs. Donc :

- pas de framework, pas de base de données, pas de traceur ni de cookie ;
- trois pages HTML générées à l'avance (français, anglais, arabe en droite-à-gauche) ;
- environ 35 Ko de HTML par page, polices hébergées sur le site ;
- le site fonctionne sans JavaScript. Le script ne sert qu'au thème clair/sombre, au menu mobile et au bouton « copier l'adresse ».

## Ce que j'ai vérifié

- Contraste des couleurs conforme WCAG 2.2 AA en thème clair et sombre (texte secondaire ≥ 6:1).
- Navigation complète au clavier, lien d'évitement, `prefers-reduced-motion` respecté.
- Politique de sécurité du contenu stricte (`public/_headers`) : aucun script externe, aucun style en ligne.
- Aucun numéro de téléphone publié, aucun document interne d'entreprise. Les rapports de stage sont confidentiels : ils ne sont pas dans ce dépôt.
- Les deux préparations (CompTIA Security+, AWS AI Practitioner) sont affichées comme **formations**, pas comme certifications : je n'ai pas encore passé les examens officiels.

## Structure

```
content/        textes du site, un fichier JSON par langue (fr, en, ar) + site.json
src/templates/  gabarits Jinja2 (page.html, 404.html)
src/assets/     style.css et main.js
tools/og.py     images de partage 1200×630 (rendu Chromium)
build.py        génère tout le dossier public/
public/         le site publié par Netlify (cv/ et assets/fonts/ sont posés à la main)
```

## Mettre à jour le site

```bash
pip install -r requirements.txt
python build.py          # pages, sitemap, en-têtes, icônes, QR code
python build.py --og     # + images de partage (Playwright + Chromium)
```

Pour changer un texte : modifier `content/fr.json`, puis la même clé dans `en.json` et `ar.json`, mettre à jour `date_modified` dans `site.json`, relancer `python build.py`, commit, push. Netlify publie `public/` automatiquement.

## Crédits

- Polices : [Amiri](https://github.com/aliftype/amiri) et [IBM Plex](https://github.com/IBM/plex), sous licence SIL Open Font License 1.1 (fichiers de licence dans `public/assets/fonts/`).
- Motif inspiré du zellige marocain (étoile à huit branches), dessiné en SVG pour ce site.

Le code est libre de réutilisation. Les textes, le CV et les contenus personnels restent les miens : merci de ne pas les reprendre.

Contact : dhaimihaithambusiness@gmail.com · [LinkedIn](https://www.linkedin.com/in/haitham-dhaimi-6b894b278)
