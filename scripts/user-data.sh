#!/bin/bash

# 🚀 Three-Tier AWS Application - User Data

set -e

# 🔄 Update System Packages
apt-get update -y

# 📦 Install Required Packages
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git

# 📁 Create Application Directory
APP_DIR="/opt/three-tier-app"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# 🐍 Create Python Virtual Environment
python3 -m venv venv
source "$APP_DIR/venv/bin/activate"

# 📚 Install Application Dependencies
pip install --upgrade pip
pip install flask gunicorn pymysql boto3

# ⚙️ Create Application Service
cat > /etc/systemd/system/three-tier-app.service <<EOF
[Unit]
Description=Three Tier Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 🔄 Enable and Start Application
systemctl daemon-reload
systemctl enable three-tier-app
systemctl start three-tier-app

# ❤️ Application Health Check
sleep 5
curl -f http://127.0.0.1:5000/health || true

# 📊 Check Application Status
systemctl status three-tier-app --no-pager || true

# 📝 Deployment Completion Log
echo "========================================="
echo "Three-Tier Application Started"
echo "Application Port: 5000"
echo "Health Check: /health"
echo "========================================="