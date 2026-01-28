## 🌍 Documentation Française / French Documentation

**Pour l'équipe en République Démocratique du Congo:**

Documentation complète en français avec guides de déploiement détaillés pour Linux et Windows.

---

## 📚 Guide Principal

### **[README_FR.md](../README_FR.md)** - Guide de Déploiement Complet (Linux/Ubuntu)

Guide principal recommandé pour le déploiement en production sur serveurs Linux.

**Sections Critiques :**
- ⚠️ **Intégration DHIS-2** : Configuration des 5 points de terminaison requis
- 🔄 **Migration Twilio → Meta Cloud API** : Guide de transition vers la production
- 📱 **Fonctionnalité Code QR** : Guide d'activation optionnel
- 🌍 **Environnements de Déploiement** : Twilio (test) vs Meta (production)

**Contenu Complet :**
- ✅ Inscription avec Meta/Twilio (WhatsApp Business API)
- ✅ Configuration serveur Ubuntu/Linux
- ✅ Installation PostgreSQL et Nginx
- ✅ Configuration SSL avec Let's Encrypt
- ✅ Déploiement en production
- ✅ Tests et validation
- ✅ Maintenance et surveillance

---

## 🪟 Guide Complémentaire Windows

### **[README_FR_WINDOWS_ADDENDUM.md](README_FR_WINDOWS_ADDENDUM.md)** - Addendum Windows Server

Guide complémentaire pour déploiement sur Windows Server 2019/2022.

**Utiliser ce guide si :**
- Vous avez une infrastructure Windows Server existante
- Des politiques informatiques nécessitent Windows
- Vous préférez IIS à Nginx

**Différences Windows Couvertes :**
- Configuration IIS (proxy inverse)
- Service Windows avec NSSM
- Certificats SSL (win-acme ou commercial)
- PowerShell au lieu de bash
- Gestion des services Windows
- Dépannage spécifique à Windows

**Note Importante :** Ce guide couvre UNIQUEMENT les différences Windows. Pour l'inscription Meta, DHIS-2, codes QR, et migration, consultez le guide principal.

---

## 📋 Fichiers Archivés

Les versions précédentes de la documentation sont dans `archive/` :

- `archive/README_FR.md` - Version antérieure (janvier 2025)
- `archive/README_FR.pdf` - Version PDF antérieure

**Ces fichiers sont obsolètes.** Utilisez le [README_FR.md](../README_FR.md) actuel à la racine du projet.

---

## 💡 Recommandation de Déploiement

### **Option Recommandée : Linux (Ubuntu 22.04 LTS)**

**Pourquoi Linux ?**
- ✅ Gratuit (pas de licence)
- ✅ Plus stable pour les services 24/7
- ✅ Meilleures performances
- ✅ Documentation plus abondante
- ✅ Communauté plus large
- ✅ Coûts d'hébergement cloud inférieurs

**Coûts Comparatifs :**
- Serveur Linux cloud : ~12-24 USD/mois (DigitalOcean, AWS)
- Serveur Windows cloud : ~40-80 USD/mois (+ licence)

### **Option Alternative : Windows Server**

Utilisez Windows Server si :
- Infrastructure Windows existante déjà en place
- Équipe IT familière uniquement avec Windows
- Politiques d'entreprise nécessitant Windows
- Intégration avec Active Directory requise

---

## 🚀 Démarrage Rapide

### Pour Déploiement Linux :
1. Consultez [README_FR.md](../README_FR.md)
2. Suivez les sections dans l'ordre
3. Commencez par Twilio (test) puis migrez vers Meta (production)

### Pour Déploiement Windows :
1. Lisez d'abord [README_FR.md](../README_FR.md) sections 1-5 (aperçu, environnements, prérequis, Meta, DHIS-2)
2. Puis suivez [README_FR_WINDOWS_ADDENDUM.md](README_FR_WINDOWS_ADDENDUM.md) pour l'installation Windows
3. Revenez au guide principal pour les codes QR et la migration

---

## 🔗 Navigation Rapide

| Section | Guide Linux | Guide Windows |
|---------|-------------|---------------|
| **Aperçu du Système** | [README_FR.md](../README_FR.md#aperçu) | Identique |
| **Environnements** | [README_FR.md](../README_FR.md#environnements-de-déploiement) | Identique |
| **Inscription Meta/Twilio** | [README_FR.md](../README_FR.md#inscription-meta-api-whatsapp-business) | Identique |
| **Intégration DHIS-2** | [README_FR.md](../README_FR.md#intégration-dhis-2) | Identique |
| **Installation Serveur** | [README_FR.md](../README_FR.md#configuration-du-serveur) | [Addendum Windows](README_FR_WINDOWS_ADDENDUM.md#installation-de-lapplication-windows) |
| **Service Système** | [README_FR.md](../README_FR.md#déploiement-en-production) (systemd) | [Addendum Windows](README_FR_WINDOWS_ADDENDUM.md#déploiement-en-production-windows) (NSSM) |
| **Proxy Inverse** | [README_FR.md](../README_FR.md#déploiement-en-production) (Nginx) | [Addendum Windows](README_FR_WINDOWS_ADDENDUM.md#étape-2--configurer-iis-comme-proxy-inverse) (IIS) |
| **Codes QR** | [README_FR.md](../README_FR.md#fonctionnalité-code-qr-optionnel) | Identique |
| **Migration Meta** | [README_FR.md](../README_FR.md#migration-de-twilio-vers-lapi-cloud-meta) | Identique |
| **Dépannage** | [README_FR.md](../README_FR.md#dépannage) | [Addendum Windows](README_FR_WINDOWS_ADDENDUM.md#dépannage-spécifique-à-windows) |

---

## ⚠️ Points Critiques Avant Déploiement

**Ne déployez PAS en production sans :**

1. ✅ Configurer les 5 points de terminaison DHIS-2 réels (voir [Intégration DHIS-2](../README_FR.md#intégration-dhis-2))
2. ✅ Tester tous les points de terminaison DHIS-2
3. ✅ Obtenir un certificat SSL valide (Let's Encrypt ou commercial)
4. ✅ Configurer un domaine avec DNS approprié
5. ✅ Tester le flux complet de génération de CIU
6. ✅ Vérifier la détection des doublons

---

## 📞 Support

Pour des questions ou problèmes :
- Consultez d'abord les sections Dépannage des guides
- Vérifiez les journaux d'application
- Contactez votre équipe technique locale
- Ouvrez une issue GitHub si nécessaire

---

**Dernière Mise à Jour :** Janvier 2026
**Version Documentation :** 2.0
