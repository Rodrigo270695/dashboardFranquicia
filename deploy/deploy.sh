#!/bin/bash
set -e

APP_DIR="/var/www/dashboard-franquicia"

echo "==> Actualizando código..."
cd "$APP_DIR"
git pull origin main

echo "==> Backend..."
cd "$APP_DIR/backend"
source venv/bin/activate
pip install -r requirements.txt -q
systemctl restart dashboard-franquicia-api

echo "==> Frontend..."
cd "$APP_DIR/frontend"
npm install
npm run build
systemctl restart dashboard-franquicia-web

echo "==> Deploy OK: $(date)"
systemctl is-active dashboard-franquicia-api
systemctl is-active dashboard-franquicia-web
