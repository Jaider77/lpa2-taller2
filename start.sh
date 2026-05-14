#!/bin/bash

echo "🚀 Iniciando Sistema de Facturas..."
echo ""

# Colores para terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

echo -e "${BLUE}📦 Construyendo imágenes Docker...${NC}"
docker-compose build

echo ""
echo -e "${BLUE}🐳 Iniciando contenedores...${NC}"
docker-compose up

echo ""
echo -e "${GREEN}✅ Sistema iniciado correctamente!${NC}"
echo ""
echo "📍 Accede a los servicios en:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   Historial: http://localhost:3000/historial"
echo "   API:       http://localhost:8000/docs"
echo ""
echo "🛑 Presiona Ctrl+C para detener los servicios"
