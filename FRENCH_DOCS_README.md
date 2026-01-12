## 🌍 Documentation Française / French Documentation

**Pour l'équipe en République Démocratique du Congo:**

Nous avons créé une documentation complète en français avec des guides de déploiement détaillés:

### 📚 Guides disponibles

1. **[README_FR.md](README_FR.md)** - Guide de déploiement complet pour **serveurs Linux (Ubuntu)**
   - Configuration serveur Ubuntu
   - Installation PostgreSQL
   - Configuration Nginx avec SSL
   - Déploiement en production
   - 1,880 lignes de documentation détaillée

2. **[README_FR_WINDOWS.md](README_FR_WINDOWS.md)** - Guide de déploiement complet pour **Windows Server 2019/2022**
   - Configuration Windows Server
   - Installation avec IIS (Internet Information Services)
   - Service Windows avec NSSM
   - Configuration SSL (Let's Encrypt ou certificat commercial)
   - 753 lignes de documentation détaillée

3. **[PDF_CONVERSION_GUIDE.md](PDF_CONVERSION_GUIDE.md)** - Instructions pour convertir la documentation en PDF professionnel

### 🎨 Conversion en PDF

Pour créer des PDFs professionnels de la documentation:

```bash
# Installation Pandoc (une seule fois)
brew install pandoc  # macOS
# ou
sudo apt install pandoc  # Ubuntu

# Conversion automatique
chmod +x convert-to-pdf.sh
./convert-to-pdf.sh

# Ou manuellement
pandoc README_FR.md -o README_FR.pdf --css=pandoc-pdf-style.css --toc --number-sections
```

### 📋 Contenu des guides français

Les deux guides incluent:
- ✅ Enregistrement avec Meta/Twilio (WhatsApp Business API)
- ✅ Configuration complète du serveur
- ✅ Installation pas-à-pas avec commandes prêtes à copier
- ✅ Configuration des variables d'environnement
- ✅ Déploiement en production
- ✅ Tests et validation
- ✅ Procédures de maintenance
- ✅ Dépannage complet
- ✅ Tous les placeholders marqués pour l'équipe canadienne

### 💡 Choix du guide

- **Linux recommandé** pour stabilité, performance et économie
- **Windows Server** fonctionne aussi très bien si c'est votre infrastructure existante
- Les deux guides sont complets et prêts pour la production

---
