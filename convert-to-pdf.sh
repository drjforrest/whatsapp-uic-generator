#!/bin/bash

# PDF Conversion Script for WhatsApp UIC Generator Documentation
# Converts French markdown documentation to professional PDF

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Convertisseur PDF - Documentation CIU WhatsApp      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}❌ Erreur: Pandoc n'est pas installé${NC}"
    echo ""
    echo "Installation de Pandoc:"
    echo "  macOS:   brew install pandoc"
    echo "  Ubuntu:  sudo apt install pandoc"
    echo "  Windows: https://pandoc.org/installing.html"
    echo ""
    exit 1
fi

# Check if pdflatex is available (better PDF quality)
if command -v pdflatex &> /dev/null; then
    PDF_ENGINE="pdflatex"
    echo -e "${GREEN}✓${NC} Utilisation de pdflatex (haute qualité)"
else
    PDF_ENGINE="wkhtmltopdf"
    echo -e "${BLUE}ℹ${NC} Utilisation de wkhtmltopdf (pdflatex recommandé pour meilleure qualité)"
fi

# Function to convert a markdown file to PDF
convert_to_pdf() {
    local input_file="$1"
    local output_file="${input_file%.md}.pdf"
    
    echo ""
    echo -e "${BLUE}📄 Conversion: ${input_file}${NC}"
    
    if [ ! -f "$input_file" ]; then
        echo -e "${RED}❌ Fichier non trouvé: ${input_file}${NC}"
        return 1
    fi
    
    # Pandoc command with all options
    pandoc "$input_file" \
        -o "$output_file" \
        --pdf-engine="$PDF_ENGINE" \
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
        --metadata date="$(date '+%B %Y')" \
        2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Succès: ${output_file}${NC}"
        echo -e "  Taille: $(du -h "$output_file" | cut -f1)"
        return 0
    else
        echo -e "${RED}❌ Échec de la conversion${NC}"
        return 1
    fi
}

# Main conversion
echo ""
echo "Fichiers disponibles pour conversion:"
echo "  1. README_FR.md (Guide Linux/Ubuntu)"
echo "  2. README_FR_WINDOWS.md (Guide Windows Server)"
echo "  3. Les deux"
echo ""
read -p "Choisissez une option (1-3): " choice

case $choice in
    1)
        convert_to_pdf "README_FR.md"
        ;;
    2)
        convert_to_pdf "README_FR_WINDOWS.md"
        ;;
    3)
        convert_to_pdf "README_FR.md"
        convert_to_pdf "README_FR_WINDOWS.md"
        ;;
    *)
        echo -e "${RED}❌ Option invalide${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Conversion terminée!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "Les fichiers PDF sont prêts à être partagés avec l'équipe en RDC."
echo ""
