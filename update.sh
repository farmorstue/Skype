#!/bin/bash
cd /root/Skype
echo "📦 Henter seneste version fra GitHub..."
git pull

echo "🐍 Aktiverer venv og installerer pakker..."
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "🔁 Genstarter bot via systemd..."
systemctl restart skype

echo "✅ Opdatering færdig!"