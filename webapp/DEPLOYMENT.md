# 🚀 Deployment Guide - bTeam WebApp

## Panoramica

Questa guida descrive come deployare bTeam WebApp in vari ambienti.

## 📦 Requisiti di Sistema

- Python 3.8 o superiore
- 512 MB RAM minimo (1 GB consigliato)
- 100 MB spazio disco
- Accesso a Internet (per Intervals.icu sync)

## 🏠 Deployment Locale (Development)

### Windows

```bash
# 1. Clona o copia il repository
cd bTeam/webapp

# 2. Crea virtual environment (opzionale ma consigliato)
python -m venv venv
venv\Scripts\activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Avvia il server
python backend/app.py
```

### Linux/Mac

```bash
# 1. Naviga nella cartella webapp
cd bTeam/webapp

# 2. Crea virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Avvia il server
python backend/app.py
```

L'applicazione sarà disponibile su: **http://localhost:8000**

## 🌐 Deployment Produzione

### Opzione 1: Uvicorn con Systemd (Linux)

1. **Crea file di servizio systemd**

```bash
sudo nano /etc/systemd/system/bteam.service
```

Contenuto:

```ini
[Unit]
Description=bTeam WebApp
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/bteam/webapp
Environment="PATH=/var/www/bteam/webapp/venv/bin"
ExecStart=/var/www/bteam/webapp/venv/bin/uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Abilita e avvia il servizio**

```bash
sudo systemctl daemon-reload
sudo systemctl enable bteam
sudo systemctl start bteam
sudo systemctl status bteam
```

### Opzione 2: Nginx + Uvicorn

1. **Configura Uvicorn (come sopra)**

2. **Configura Nginx come reverse proxy**

```bash
sudo nano /etc/nginx/sites-available/bteam
```

Contenuto:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/bteam/webapp/static;
    }
}
```

3. **Abilita sito e riavvia Nginx**

```bash
sudo ln -s /etc/nginx/sites-available/bteam /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Opzione 3: Docker

1. **Crea Dockerfile**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copia requirements e installa dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia applicazione
COPY . .

# Esponi porta
EXPOSE 8000

# Avvia applicazione
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

2. **Crea docker-compose.yml**

```yaml
version: '3.8'

services:
  webapp:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
```

3. **Avvia con Docker**

```bash
docker-compose up -d
```

### Opzione 4: Heroku

1. **Crea Procfile**

```
web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT --workers 2
```

2. **Deploy**

```bash
heroku login
heroku create bteam-app
git push heroku main
```

## 🔒 Configurazione Sicurezza

### 1. HTTPS (SSL/TLS)

**Con Nginx + Let's Encrypt:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. CORS

Modifica `backend/app.py` per specificare origini esatte:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specifica domini esatti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Firewall

```bash
# Apri solo porta 80 e 443
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. Database Backup

```bash
# Crea script di backup giornaliero
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /var/www/bteam/webapp/data/bteam.db /backups/bteam_$DATE.db

# Mantieni solo ultimi 30 backup
find /backups -name "bteam_*.db" -mtime +30 -delete
```

## ⚙️ Variabili d'Ambiente

Crea file `.env` per configurazioni:

```bash
# Database
DATABASE_PATH=/var/www/bteam/webapp/data

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/bteam/app.log

# CORS
ALLOWED_ORIGINS=https://your-domain.com
```

## 📊 Monitoraggio

### 1. Logs

```bash
# Systemd logs
sudo journalctl -u bteam -f

# Application logs
tail -f /var/log/bteam/app.log
```

### 2. Health Check

Configura un health check endpoint:

```python
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

### 3. Monitoring Tools

- **Prometheus + Grafana** per metriche
- **Sentry** per error tracking
- **UptimeRobot** per uptime monitoring

## 🔧 Troubleshooting

### "Permission denied" su porta 80

Usa porta superiore (8000) e Nginx come proxy, oppure:

```bash
sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3
```

### Database locked

Assicurati che solo un processo acceda al database:

```bash
# Verifica processi
ps aux | grep uvicorn

# Kill processi multipli se necessario
```

### Memoria insufficiente

Riduci numero di workers:

```bash
uvicorn backend.app:app --workers 2
```

## 🚀 Performance Optimization

### 1. Static Files Caching

Nginx:

```nginx
location /static {
    alias /var/www/bteam/webapp/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 2. Gzip Compression

Nginx:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 3. Database Optimization

```bash
# Vacuum database periodicamente
sqlite3 data/bteam.db "VACUUM;"
```

## 📱 Mobile Access

L'interfaccia è responsive e funziona su mobile. Per accesso esterno:

1. Configura port forwarding sul router (porta 8000 o 80/443)
2. Usa servizio DDNS se IP dinamico
3. Considera VPN per accesso sicuro

## 🔄 Update Process

```bash
# 1. Backup database
cp data/bteam.db data/bteam.db.backup

# 2. Pull nuove modifiche
git pull

# 3. Aggiorna dipendenze
pip install -r requirements.txt --upgrade

# 4. Riavvia servizio
sudo systemctl restart bteam
```

## 📋 Checklist Pre-Deployment

- [ ] Testato localmente
- [ ] Database backup configurato
- [ ] HTTPS configurato (produzione)
- [ ] CORS configurato correttamente
- [ ] Firewall configurato
- [ ] Logs funzionanti
- [ ] Health check funzionante
- [ ] Performance testata
- [ ] Documentazione aggiornata

---

**Best Practice**: Testa sempre in ambiente di staging prima del deployment in produzione.
