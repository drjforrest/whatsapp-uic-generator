#!/bin/bash
# Development server runner script

set -e

echo "🚀 Starting WhatsApp UIC Generator (Development Mode)"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if database exists
if [ ! -f uic_database.db ]; then
    echo "⚠️  Warning: Database not initialized"
    echo "   Run: python scripts/init_db.py"
    echo ""
    read -p "Initialize database now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python scripts/init_db.py
    else
        echo "   Continuing without database initialization..."
    fi
    echo ""
fi

echo "📋 Configuration:"
echo "   • Environment: $(grep ENVIRONMENT .env | cut -d '=' -f2)"
echo "   • Log Level: $(grep LOG_LEVEL .env | cut -d '=' -f2)"
echo "   • Debug: $(grep DEBUG .env | cut -d '=' -f2)"
echo ""

echo "🌐 Server will start at: http://localhost:8000"
echo "📚 API Docs will be at: http://localhost:8000/docs"
echo ""

echo "💡 Tips:"
echo "   • Press Ctrl+C to stop the server"
echo "   • In another terminal, run: ngrok http 8000"
echo "   • Use the ngrok URL in Twilio webhook config"
echo ""

echo "Starting server..."
echo ""

# Start uvicorn with reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
