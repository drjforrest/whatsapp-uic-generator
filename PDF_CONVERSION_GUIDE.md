# Guide de Conversion PDF - Documentation CIU WhatsApp

Instructions pour convertir la documentation Markdown en PDF professionnel pour distribution.

---

## 📋 Fichiers créés

1. **pandoc-pdf-style.css** - Feuille de style CSS professionnelle
2. **convert-to-pdf.sh** - Script de conversion automatique
3. Ce guide - Instructions d'utilisation

---

## 🔧 Installation de Pandoc

### macOS
```bash
# Avec Homebrew
brew install pandoc

# Avec MacPorts
sudo port install pandoc

# Pour une qualité PDF optimale, installez aussi:
brew install basictex
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install pandoc texlive-latex-base texlive-fonts-recommended
```

### Windows
1. Téléchargez depuis: https://pandoc.org/installing.html
2. Exécutez l'installateur
3. Redémarrez votre terminal/PowerShell

### Vérifier l'installation
```bash
pandoc --version
```

---

## 🚀 Méthode 1: Utiliser le script automatique (Recommandé)

### Sur macOS/Linux:

```bash
# Rendre le script exécutable (une seule fois)
chmod +x convert-to-pdf.sh

# Exécuter le script
./convert-to-pdf.sh
```

Le script vous proposera:
1. Convertir README_FR.md (Guide Linux)
2. Convertir README_FR_WINDOWS.md (Guide Windows)
3. Convertir les deux

### Sur Windows (PowerShell):

```powershell
# Convertir le guide Linux
pandoc README_FR.md -o README_FR.pdf --css=pandoc-pdf-style.css --toc --number-sections

# Convertir le guide Windows
pandoc README_FR_WINDOWS.md -o README_FR_WINDOWS.pdf --css=pandoc-pdf-style.css --toc --number-sections
```

---

## 📝 Méthode 2: Conversion manuelle avec Pandoc

### Commande de base (bonne qualité)

```bash
pandoc README_FR.md \
  -o README_FR.pdf \
  --css=pandoc-pdf-style.css \
  --toc \
  --number-sections
```

### Commande avancée (haute qualité, recommandée)

```bash
pandoc README_FR.md \
  -o README_FR.pdf \
  --pdf-engine=pdflatex \
  --css=pandoc-pdf-style.css \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --highlight-style=tango \
  --variable urlcolor=blue \
  --variable linkcolor=blue \
  --variable geometry:margin=2.5cm \
  --variable geometry:top=3cm \
  --variable geometry:bottom=3cm \
  --variable fontsize=11pt \
  --variable documentclass=article \
  --variable papersize=letter \
  --variable lang=fr \
  --variable mainlang=french \
  --metadata title="Guide de Déploiement - Générateur de CIU WhatsApp" \
  --metadata author="Health Equity & Resilience Observatory (HERO), UBC" \
  --metadata date="Janvier 2026"
```

### Pour le guide Windows:

Remplacez simplement `README_FR.md` par `README_FR_WINDOWS.md` et `README_FR.pdf` par `README_FR_WINDOWS.pdf`.

---

## 🎨 Personnalisation du style

Le fichier `pandoc-pdf-style.css` contient tous les styles. Vous pouvez le modifier pour changer:

### Couleurs principales
```css
/* Ligne 83-84 : Couleurs des titres */
color: #0066cc;  /* Bleu principal */
border-bottom: 3px solid #0066cc;
```

### Taille de police
```css
/* Ligne 20 : Taille du texte de base */
font-size: 11pt;  /* Changez à 10pt pour texte plus petit, 12pt pour plus grand */
```

### Marges de page
```css
/* Ligne 11 : Marges */
margin: 2.5cm 2cm 2.5cm 2cm;  /* haut, droite, bas, gauche */
```

### Couleur des boîtes d'information
```css
/* Lignes 348-388 : Boîtes spéciales */
background-color: #d4edda;  /* Vert pour succès */
background-color: #fff3cd;  /* Jaune pour avertissement */
background-color: #f8d7da;  /* Rouge pour danger */
background-color: #e7f3ff;  /* Bleu pour notes */
```

---

## 🔍 Options de Pandoc expliquées

| Option | Description |
|--------|-------------|
| `--pdf-engine=pdflatex` | Moteur PDF (pdflatex donne la meilleure qualité) |
| `--css=pandoc-pdf-style.css` | Utilise notre feuille de style |
| `--toc` | Génère une table des matières |
| `--toc-depth=3` | Profondeur de la table des matières (h1, h2, h3) |
| `--number-sections` | Numérotation automatique des sections |
| `--highlight-style=tango` | Style de coloration syntaxique du code |
| `--variable geometry:margin=2.5cm` | Marges du document |
| `--variable fontsize=11pt` | Taille de police |
| `--variable lang=fr` | Langue du document (césure française) |
| `--metadata title="..."` | Métadonnées du PDF |

---

## 📊 Résultat attendu

Après conversion, vous obtiendrez un PDF avec:

✅ **Page de titre professionnelle**
- Titre du document
- Sous-titre
- Auteur et organisation
- Date

✅ **Table des matières complète**
- Toutes les sections numérotées
- Liens cliquables vers chaque section

✅ **Formatage professionnel**
- Titres en bleu avec bordures
- Boîtes colorées pour avertissements/notes
- Code avec coloration syntaxique
- Tableaux formatés
- Liens cliquables

✅ **En-têtes et pieds de page**
- Nom du document en en-tête
- Numéros de page en pied de page

✅ **Optimisations impression**
- Évite les coupures de page inappropriées
- Marges adaptées à l'impression
- Qualité professionnelle

---

## 🐛 Dépannage

### Erreur: "pandoc: command not found"
**Solution:** Installez Pandoc (voir section Installation)

### Erreur: "pdflatex not found"
**Solution:** 
```bash
# macOS
brew install basictex

# Ubuntu
sudo apt install texlive-latex-base texlive-fonts-recommended

# Ou utilisez un autre moteur:
pandoc README_FR.md -o README_FR.pdf --pdf-engine=wkhtmltopdf --css=pandoc-pdf-style.css
```

### Le CSS ne s'applique pas correctement
**Solution:** Assurez-vous que `pandoc-pdf-style.css` est dans le même dossier que votre fichier markdown.

### Les accents français ne s'affichent pas
**Solution:** Ajoutez les options de langue:
```bash
--variable lang=fr --variable mainlang=french
```

### Le PDF est trop volumineux
**Solution:** 
```bash
# Après génération, compressez avec:
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=README_FR_compressed.pdf README_FR.pdf
```

### Les emojis ne s'affichent pas
**Solution:** C'est normal avec pdflatex. Les emojis seront convertis en texte. Si vous voulez les garder, utilisez:
```bash
--pdf-engine=wkhtmltopdf
```

---

## 📤 Partage avec l'équipe RDC

### Par email:
Les PDFs générés sont optimisés pour l'email (généralement 1-3 MB).

### Via cloud:
1. Google Drive
2. Dropbox
3. OneDrive

### Impression:
Les PDFs sont optimisés pour impression format Letter (8.5" x 11") ou A4.

---

## 🔄 Mise à jour des PDFs

Après toute modification des fichiers markdown:

```bash
# Méthode rapide (script automatique)
./convert-to-pdf.sh

# Ou manuellement
pandoc README_FR.md -o README_FR.pdf --css=pandoc-pdf-style.css --toc --number-sections
```

---

## 💡 Conseils pour la documentation

### Avant conversion:

1. **Vérifiez les liens** - Tous les liens doivent être corrects
2. **Testez les placeholders** - Assurez-vous que tous les `[À COMPLÉTER PAR L'ÉQUIPE CANADIENNE]` sont bien visibles
3. **Vérifiez la numérotation** - Les sections doivent être logiquement ordonnées
4. **Relisez** - Faites une dernière vérification orthographique

### Après conversion:

1. **Ouvrez le PDF** - Vérifiez que tout s'affiche correctement
2. **Testez les liens** - Cliquez sur quelques liens pour vérifier qu'ils fonctionnent
3. **Vérifiez la table des matières** - Assurez-vous qu'elle est complète
4. **Testez l'impression** - Imprimez une page test si vous prévoyez distribuer en papier

---

## 🎓 Ressources supplémentaires

### Documentation Pandoc:
- Guide officiel: https://pandoc.org/MANUAL.html
- PDF avec LaTeX: https://pandoc.org/MANUAL.html#creating-a-pdf

### Styles CSS pour Pandoc:
- Guide CSS: https://pandoc.org/MANUAL.html#css
- Exemples: https://github.com/jgm/pandoc/wiki/User-contributed-templates

---

## 📞 Support

Si vous rencontrez des problèmes avec la conversion:

1. Vérifiez que Pandoc est à jour: `pandoc --version`
2. Consultez les logs d'erreur complets
3. Testez avec une commande simple d'abord
4. Contactez l'équipe technique si nécessaire

---

**Créé par:** Jamie Forrest, PhD, MPH  
**Organisation:** Health Equity & Resilience Observatory (HERO), UBC  
**Dernière mise à jour:** Janvier 2026
