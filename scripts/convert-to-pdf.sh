#!/bin/bash

# PDF Conversion Script for WhatsApp UIC Generator Documentation
# Handles emoji removal for LaTeX compatibility

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PDF Converter - WhatsApp UIC Generator Docs         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}❌ Error: Pandoc is not installed${NC}"
    echo ""
    echo "Installing Pandoc:"
    echo "  macOS:   brew install pandoc"
    echo "  Ubuntu:  sudo apt install pandoc"
    echo "  Windows: https://pandoc.org/installing.html"
    echo ""
    exit 1
fi

# Check if pdflatex is available
if command -v pdflatex &> /dev/null; then
    PDF_ENGINE="pdflatex"
    echo -e "${GREEN}✓${NC} Using pdflatex (high quality)"
    USE_LATEX=true
else
    PDF_ENGINE="wkhtmltopdf"
    echo -e "${BLUE}ℹ${NC} Using wkhtmltopdf"
    USE_LATEX=false
fi

# Function to remove emojis from markdown (LaTeX compatibility)
remove_emojis() {
    local input_file="$1"
    local temp_file="${input_file%.md}_temp.md"
    
    # Remove all emojis and problematic Unicode characters
    # This covers: emojis, symbols, pictographs, transport symbols, flags, etc.
    perl -CSD -Mutf8 -pe '
        s/[\x{1F300}-\x{1F9FF}]//g;  # Misc Symbols and Pictographs, Emoticons, Transport, etc
        s/[\x{2600}-\x{26FF}]//g;    # Misc symbols
        s/[\x{2700}-\x{27BF}]//g;    # Dingbats
        s/[\x{1F000}-\x{1F02F}]//g;  # Mahjong Tiles
        s/[\x{1F0A0}-\x{1F0FF}]//g;  # Playing Cards
        s/[\x{1F100}-\x{1F64F}]//g;  # Enclosed characters
        s/[\x{1F680}-\x{1F6FF}]//g;  # Transport and Map Symbols
        s/[\x{1F900}-\x{1F9FF}]//g;  # Supplemental Symbols
        s/[\x{2300}-\x{23FF}]//g;    # Miscellaneous Technical
        s/[\x{FE00}-\x{FE0F}]//g;    # Variation Selectors
        s/[\x{200D}]//g;             # Zero Width Joiner
    ' "$input_file" > "$temp_file"
    
    echo "$temp_file"
}

# Function to convert a markdown file to PDF
convert_to_pdf() {
    local input_file="$1"
    local output_file="${input_file%.md}.pdf"
    
    echo ""
    echo -e "${BLUE}📄 Conversion: ${input_file}${NC}"
    
    if [ ! -f "$input_file" ]; then
        echo -e "${RED}❌ File not found: ${input_file}${NC}"
        return 1
    fi
    
    # Prepare input (remove emojis for LaTeX)
    if [ "$USE_LATEX" = true ]; then
        echo -e "${BLUE}   → Preparing for LaTeX (removing emojis)${NC}"
        local processed_file=$(remove_emojis "$input_file")
    else
        local processed_file="$input_file"
    fi
    
    # Pandoc command
    if [ "$USE_LATEX" = true ]; then
        # LaTeX-based conversion (high quality)
        pandoc "$processed_file" \
            -o "$output_file" \
            --pdf-engine=pdflatex \
            --from=markdown-yaml_metadata_block \
            -V colorlinks=true \
            -V linkcolor=blue \
            -V urlcolor=blue \
            --variable geometry:margin=2cm \
            --variable geometry:top=2.5cm \
            --variable geometry:bottom=2.5cm \
            --variable geometry:left=2cm \
            --variable geometry:right=2cm \
            --toc \
            --toc-depth=3 \
            --number-sections \
            --variable fontsize=10pt \
            --variable documentclass=article \
            --variable papersize=letter \
            --variable lang=en \
            --variable mainlang=english \
            --metadata title="Deployment Guide - WhatsApp UIC Generator" \
            --metadata subtitle="For Deployment of UIC Generation to Support DHIS-2 Tracker in the Democratic Republic of the Congo (DRC)" \
            --metadata date="$(date '+%B %Y')" \
            2>&1
    else
        # HTML-based conversion
        pandoc "$processed_file" \
            -o "$output_file" \
            --from=markdown-yaml_metadata_block \
            --css=pandoc-pdf-style.css \
            --toc \
            --toc-depth=3 \
            --number-sections \
            --variable urlcolor=blue \
            --variable linkcolor=blue \
            --metadata title="Deployment Guide - WhatsApp UIC Generator" \
            --metadata subtitle="For Deployment of UIC Generation to Support DHIS-2 Tracker in the Democratic Republic of the Congo (DRC)" \
            --metadata date="$(date '+%B %Y')" \
            2>&1
    fi
    
    local exit_code=$?
    
    # Cleanup temp file
    if [ "$USE_LATEX" = true ] && [ -f "$processed_file" ]; then
        rm -f "$processed_file"
    fi
    
    if [ $exit_code -eq 0 ] && [ -f "$output_file" ]; then
        echo -e "${GREEN}✓ Success: ${output_file}${NC}"
        echo -e "  Size: $(du -h "$output_file" | cut -f1)"
        return 0
    else
        echo -e "${RED}❌ Conversion failed${NC}"
        return 1
    fi
}

# Main conversion
echo ""
echo "Converting README.md to PDF..."
echo ""
read -p "Proceed with conversion? (y/n): " choice

case $choice in
    [Yy]*)
        convert_to_pdf "README.md"
        ;;
    *)
        echo -e "${RED}❌ Conversion cancelled${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Conversion complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "PDF is ready to share with the DRC team."
echo ""
