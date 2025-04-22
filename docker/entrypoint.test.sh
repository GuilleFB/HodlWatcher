#!/bin/bash

set -e  # Stop the script if any command fails (you can delete it if you want the script to keep running in case of errors)

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # no color

echo -e "${CYAN}🚀 Initiating analysis and testing...${NC}"
echo ""

echo -e "${YELLOW}🔍 Waiting for Redis to be ready...${NC}"
wait-for-it redis:6379 --timeout=60 --strict -- echo "→ Redis is ready"
echo ""

echo -e "${YELLOW}🔍 Waiting for Postgres to be ready...${NC}"
wait-for-it postgres:5432 --timeout=60 --strict -- echo "→ PostgreSQL is ready"
echo ""

echo -e "${YELLOW}🔍 BANDIT: Security Analysis${NC}"
bandit -r . -ll || true
echo ""

echo -e "${YELLOW}📦 SAFETY: Checking dependencies${NC}"
cd ..
safety check || true
cd srv
echo ""

echo -e "${CYAN}⚙️ Initializing Django...${NC}"
python manage.py check || { echo -e "${RED}❌ Django check failed.${NC}"; exit 1; }
echo ""

# Running Django migrations
echo -e "${CYAN}🔄 Running migrations...${NC}"
python manage.py migrate --noinput
echo ""

echo -e "${YELLOW}🧪 PYTEST & COVERAGE: Running tests${NC}"
coverage run -m pytest -n auto --cache-clear --cipdb --flake8 --black . || { echo -e "${RED}❌ Pytest found errors.${NC}"; exit 1; }
echo ""
coverage report
echo ""
echo -e "${GREEN}✅ Tests successfully completed.${NC}"
echo ""

echo -e "${GREEN}🎉 SECURITY TEST COMPLETED 🎉${NC}"
echo -e "⚡ ${YELLOW}Please review the analysis..${NC} ⚡"
