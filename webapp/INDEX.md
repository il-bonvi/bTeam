# 🚴 bTeam WebApp - Navigation Guide

## 🎯 Quick Access

| What do you need? | Go to... |
|-------------------|----------|
| **Get Started Immediately** | [QUICK_START.md](QUICK_START.md) |
| **Full Overview** | [README.md](README.md) |
| **Deploy to Production** | [DEPLOYMENT.md](DEPLOYMENT.md) |
| **API Documentation** | [api_docs/API_REFERENCE.md](api_docs/API_REFERENCE.md) |
| **Intervals.icu Sync** | [api_docs/INTERVALS_INTEGRATION.md](api_docs/INTERVALS_INTEGRATION.md) |
| **Future Plans** | [ROADMAP.md](ROADMAP.md) |
| **Project Summary** | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |

---

## 📚 Documentation Index

### For New Users
1. **[QUICK_START.md](QUICK_START.md)** ⚡
   - Get running in 3 steps
   - First team setup
   - First athlete creation
   - Intervals.icu sync guide

2. **[README.md](README.md)** 📖
   - Complete feature overview
   - Installation instructions
   - Usage examples
   - Troubleshooting

### For Developers
3. **[api_docs/API_REFERENCE.md](api_docs/API_REFERENCE.md)** 🔧
   - All 30+ API endpoints
   - Request/response examples
   - Error codes
   - Testing with Swagger UI

4. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** 📊
   - Technical overview
   - Architecture details
   - Technology stack
   - Performance metrics

### For System Administrators
5. **[DEPLOYMENT.md](DEPLOYMENT.md)** 🚀
   - Multiple deployment options
   - Security configuration
   - Performance tuning
   - Monitoring setup

### For Intervals.icu Users
6. **[api_docs/INTERVALS_INTEGRATION.md](api_docs/INTERVALS_INTEGRATION.md)** 🔄
   - How to get API key
   - Sync activities guide
   - Sync wellness guide
   - Push races to Intervals.icu

### For Planning
7. **[ROADMAP.md](ROADMAP.md)** 🗺️
   - Completed features
   - Future enhancements
   - Timeline estimates
   - Feature requests

---

## 🏗️ Project Structure

```
webapp/
│
├── 📄 Documentation (You are here!)
│   ├── README.md                 # Main documentation
│   ├── QUICK_START.md           # Quick start guide
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── ROADMAP.md               # Future plans
│   ├── PROJECT_SUMMARY.md       # Project overview
│   ├── requirements.txt         # Python dependencies
│   └── INDEX.md                 # This file
│
├── 📁 api_docs/                 # API Documentation
│   ├── API_REFERENCE.md         # Complete API reference
│   └── INTERVALS_INTEGRATION.md # Intervals.icu guide
│
├── 🔧 backend/                  # Backend Application
│   ├── app.py                   # Main FastAPI app
│   └── __init__.py
│
├── 📦 modules/                  # Functional Modules
│   ├── teams/                   # Team management
│   │   └── backend/
│   │       └── teams_routes.py
│   ├── athletes/                # Athlete management
│   │   └── backend/
│   │       └── athletes_routes.py
│   ├── activities/              # Activity tracking
│   │   └── backend/
│   │       └── activities_routes.py
│   ├── races/                   # Race planning
│   │   └── backend/
│   │       └── races_routes.py
│   ├── wellness/                # Wellness tracking
│   │   └── backend/
│   │       └── wellness_routes.py
│   └── sync/                    # Intervals.icu sync
│       └── backend/
│           └── sync_routes.py
│
├── 🎨 static/                   # Static Files
│   ├── css/
│   │   └── main.css             # Main stylesheet
│   ├── js/
│   │   ├── api.js               # API client
│   │   ├── utils.js             # Utilities
│   │   ├── app.js               # Main app
│   │   ├── teams.js             # Teams module
│   │   ├── athletes.js          # Athletes module
│   │   ├── activities.js        # Activities module
│   │   ├── races.js             # Races module
│   │   ├── wellness.js          # Wellness module
│   │   └── sync.js              # Sync module
│   └── images/                  # Images
│
├── 📄 templates/                # HTML Templates
│   └── index.html               # Main page
│
├── 📂 config/                   # Configuration
│
└── 💾 data/                     # Database
    └── bteam.db                 # SQLite database (auto-created)
```

---

## 🎯 Common Tasks

### I want to...

#### ...start the application
→ See [QUICK_START.md](QUICK_START.md) - Section "Avvio Rapido"

#### ...create my first team
→ See [QUICK_START.md](QUICK_START.md) - Section "Crea la Prima Squadra"

#### ...add athletes
→ See [QUICK_START.md](QUICK_START.md) - Section "Aggiungi il Primo Atleta"

#### ...sync from Intervals.icu
→ See [api_docs/INTERVALS_INTEGRATION.md](api_docs/INTERVALS_INTEGRATION.md) - Section "Utilizzo nell'App"

#### ...deploy to production
→ See [DEPLOYMENT.md](DEPLOYMENT.md) - Choose your platform

#### ...understand the API
→ See [api_docs/API_REFERENCE.md](api_docs/API_REFERENCE.md) - Complete reference

#### ...add a new feature
→ See [ROADMAP.md](ROADMAP.md) - Future plans

---

## 🔗 External Links

- **Intervals.icu**: https://intervals.icu
- **Intervals.icu API Docs**: https://intervals.icu/api
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://www.sqlalchemy.org

---

## 📞 Help & Support

### Documentation Not Clear?
Check [README.md](README.md) FAQ section

### Technical Issues?
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) Troubleshooting section
2. Review [api_docs/API_REFERENCE.md](api_docs/API_REFERENCE.md) for API errors

### Feature Requests?
See [ROADMAP.md](ROADMAP.md) to check if already planned

---

## 🌟 Key Features at a Glance

| Feature | Status | Documentation |
|---------|--------|---------------|
| Team Management | ✅ Complete | [README.md](README.md) |
| Athlete Management | ✅ Complete | [README.md](README.md) |
| Activity Tracking | ✅ Complete | [README.md](README.md) |
| Race Planning | ✅ Complete | [README.md](README.md) |
| Wellness Tracking | ✅ Complete | [README.md](README.md) |
| Intervals.icu Sync | ✅ Complete | [api_docs/INTERVALS_INTEGRATION.md](api_docs/INTERVALS_INTEGRATION.md) |
| REST API | ✅ Complete | [api_docs/API_REFERENCE.md](api_docs/API_REFERENCE.md) |
| Responsive UI | ✅ Complete | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |

---

## 🚀 Quick Commands

```bash
# Start application
python backend/app.py

# Install dependencies
pip install -r requirements.txt

# Run with uvicorn (production)
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4

# Access application
http://localhost:8000

# Access API docs
http://localhost:8000/docs
```

---

## 📈 Version History

- **v1.0.0** (2026-02-13) - Initial release
  - Complete webapp implementation
  - All desktop features ported
  - Modern responsive UI
  - Full Intervals.icu integration

---

**Happy cycling with bTeam! 🚴‍♂️🚴‍♀️**

---

*Last Updated: 2026-02-13*  
*Documentation Version: 1.0.0*  
*Project Status: ✅ Production Ready*
