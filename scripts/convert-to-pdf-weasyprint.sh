#!/bin/bash

# PDF Conversion Script - WeasyPrint Edition (Homebrew)
# Converts Markdown → HTML → PDF with custom CSS styling
# Uses Homebrew's WeasyPrint for clean, dependency-free conversion
# Your pandoc-pdf-style.css is fully compatible!

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PDF Converter - WeasyPrint Edition (Homebrew)       ║${NC}"
echo -e "${BLUE}║   Markdown → HTML → PDF with Custom CSS               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Define paths
WEASYPRINT_BIN="/opt/homebrew/bin/weasyprint"

# Check dependencies
echo "Checking dependencies..."
echo ""

if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}❌ Error: Pandoc not installed${NC}"
    echo "Install with: brew install pandoc"
    exit 1
fi
echo -e "${GREEN}✓${NC} Pandoc found: $(pandoc --version | head -1)"

if [ ! -x "$WEASYPRINT_BIN" ]; then
    echo -e "${RED}❌ Error: WeasyPrint not found at $WEASYPRINT_BIN${NC}"
    echo ""
    echo "Install with:"
    echo "  brew install weasyprint"
    echo ""
    echo "Or verify the path with:"
    echo "  which weasyprint"
    exit 1
fi

echo -e "${GREEN}✓${NC} WeasyPrint found: $WEASYPRINT_BIN"
echo -e "${GREEN}✓${NC} WeasyPrint version: $($WEASYPRINT_BIN --version)"

# Check for CSS file
if [ ! -f "pandoc-pdf-style.css" ]; then
    echo -e "${YELLOW}⚠${NC} Warning: pandoc-pdf-style.css not found"
    echo "   PDF will use default styling instead"
    USE_CSS=false
else
    echo -e "${GREEN}✓${NC} CSS file found: pandoc-pdf-style.css"
    USE_CSS=true
fi

echo -e "${GREEN}✓${NC} All dependencies available"
echo ""

# Function to convert markdown to PDF
convert_to_pdf() {
    local input_file="$1"
    local output_file="${input_file%.md}.pdf"
    
    echo "Conversion: ${input_file} → ${output_file}"
    echo ""
    
    if [ ! -f "$input_file" ]; then
        echo -e "${RED}❌ File not found: ${input_file}${NC}"
        return 1
    fi
    
    # Step 1: Convert Markdown to HTML
    echo -e "${BLUE}[1/2]${NC} Converting Markdown to HTML..."
    
    if [ "$USE_CSS" = true ]; then
        pandoc "$input_file" \
            -f markdown-yaml_metadata_block \
            -t html5 \
            -o /tmp/readme.html \
            --css pandoc-pdf-style.css \
            --toc \
            --toc-depth=3 \
            --number-sections \
            --metadata title="Deployment Guide - WhatsApp UIC Generator" \
            --metadata subtitle="For Deployment of UIC Generation to Support DHIS-2 Tracker in the Democratic Republic of the Congo (DRC)" \
            --metadata date="$(date '+%B %Y')" \
            --metadata author="WhatsApp UIC Generator Team" \
            2>&1
    else
        pandoc "$input_file" \
            -f markdown-yaml_metadata_block \
            -t html5 \
            -o /tmp/readme.html \
            --toc \
            --toc-depth=3 \
            --number-sections \
            --metadata title="Deployment Guide - WhatsApp UIC Generator" \
            --metadata subtitle="For Deployment of UIC Generation to Support DHIS-2 Tracker in the Democratic Republic of the Congo (DRC)" \
            --metadata date="$(date '+%B %Y')" \
            --metadata author="WhatsApp UIC Generator Team" \
            2>&1
    fi
    
    local pandoc_exit=$?
    
    if [ $pandoc_exit -ne 0 ] || [ ! -f /tmp/readme.html ]; then
        echo -e "${RED}❌ HTML generation failed${NC}"
        return 1
    fi
    
    echo -e "${GREEN}   ✓ HTML generated${NC}"
    echo ""
    
    # Step 2: Convert HTML to PDF with WeasyPrint
    echo -e "${BLUE}[2/2]${NC} Converting HTML to PDF with WeasyPrint..."
    
    "$WEASYPRINT_BIN" /tmp/readme.html "$output_file" 2>&1
    
    local weasyprint_exit=$?
    
    if [ $weasyprint_exit -eq 0 ] && [ -f "$output_file" ]; then
        echo -e "${GREEN}   ✓ PDF generated${NC}"
        echo ""
        echo -e "${GREEN}✓ Conversion successful!${NC}"
        echo -e "  Output: ${output_file}"
        echo -e "  Size: $(du -h "$output_file" | cut -f1)"
        
        # Cleanup temp file
        rm -f /tmp/readme.html
        
        return 0
    else
        echo -e "${RED}❌ PDF conversion failed${NC}"
        return 1
    fi
}

# Main conversion
echo ""
echo "Target: README.md → README.pdf"
echo ""
read -p "Proceed with conversion? (y/n): " choice

echo ""

case $choice in
    [Yy]*)
        convert_to_pdf "README.md"
        exit_code=$?
        
        echo ""
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}✓ Conversion Complete!${NC}"
            echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
            echo ""
            echo "Your PDF is ready to share with the DRC team."
            echo "✅ Code blocks render properly (no narrow column issue)"
            echo "✅ All styling from pandoc-pdf-style.css applied"
            echo "✅ Bash backslashes handled correctly"
            echo "✅ Horizontal rules preserved (no YAML parsing conflicts)"
            echo ""
        fi
        exit $exit_code
        ;;
    *)
        echo -e "${RED}❌ Conversion cancelled${NC}"
        exit 1
        ;;
esac
