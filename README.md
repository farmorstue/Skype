# 🛡️ Skype Discord Bot

En avanceret Discord-bot til håndtering af gear-reaktioner, opkaldslogning og automatiseret stemmeoversigt. Bruges til organisering af spillere i fraktioner og til nem koordinering.

---

## 🚀 Funktioner

- `!geara`, `!gearb`, `!gearc` – Sender en besked med emojis, så spillere selv kan vælge deres gearstatus.
- `!react <besked-id>` – Viser hvem i opkaldet der **ikke har reageret** på beskeden.
- `!gearroll <besked-id>` – Giver hver spiller et navn i rækkefølge, baseret på deres gear.
- Logger:
  - Reaktioner og unreaktioner
  - Deltagelse i stemmekanaler
  - Bot-genstart

---

## ⚙️ Installation (på server)

### 1. Klon projektet og gå ind i mappen:
```bash
git clone https://github.com/farmorstue/Skype.git
cd Skype
```

### 2. Opret virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installér nødvendige pakker:
```bash
pip install -r requirements.txt
```

---

## 🔐 Konfiguration

### Opret `.env`-fil i projektmappen:

```env
DISCORD_TOKEN=din_token_her
```

> Denne fil **må ikke uploades til GitHub**. Den er automatisk udelukket via `.gitignore`.

---

## ▶️ Start botten manuelt

```bash
source venv/bin/activate
python main.py
```

---

## ⚙️ Kør som systemd-service (anbefalet til server)

1. Opret filen:

```ini
# /etc/systemd/system/skype.service
[Unit]
Description=Skype Discord Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/Skype
ExecStart=/root/Skype/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Genindlæs og start servicen:

```bash
systemctl daemon-reload
systemctl enable skype
systemctl start skype
```

3. Tjek status:

```bash
systemctl status skype
```

---

## 🔁 Opdatering af botten

Brug dette script (valgfrit):

```bash
./update.sh
```

Eller manuelt:

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
deactivate
systemctl restart skype
```

---

## 📂 Projektstruktur

```
Skype/
├── main.py
├── .env             # (privat – ikke i GitHub)
├── requirements.txt
├── .gitignore
├── update.sh        # (valgfri)
└── README.md
```

---

## 🛠 Krav

- Python 3.9+
- Aktiverede intents i [Discord Developer Portal](https://discord.com/developers/applications)
  - ✅ Message Content Intent
  - ✅ Server Members Intent

---

## 💬 Support

Kontakt `farmorstue` på Discord eller opret en Issue her på GitHub hvis du har spørgsmål.
