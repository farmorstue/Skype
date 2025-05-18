# Skype Discord Bot

En speciallavet Discord-bot med reaktionsstyring, gear-kategorier og systemd-support.

## Kommandoer

- `!ping` – Test kommando

## Kørsel

Startes automatisk med systemd (skype.service)

## Installation

```bash
git clone https://github.com/din-bruger/Skype.git
cd Skype
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt