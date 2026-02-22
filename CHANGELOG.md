# Changelog

All notable changes to Kasir Toko Sembako.

## [1.1.0] - 2026-02-12

### Added - Docker & CasaOS Support
- 🐳 **Docker support** untuk containerized deployment
- 📦 **CasaOS integration** untuk STB HG680P
- 📚 **Comprehensive documentation**:
  - `DEPLOYMENT_CASAOS.md` - Full deployment guide
  - `QUICKSTART_CASAOS.md` - Quick start guide
  - `DOCKER_COMMANDS.md` - Command reference
  - `DEPLOYMENT_FILES.md` - File list & checklist
- 🛠️ **Setup scripts**:
  - `setup-docker.sh` for Linux/Mac/CasaOS
  - `setup-docker.ps1` for Windows PowerShell
- ⚙️ **Configuration files**:
  - `Dockerfile` - Optimized for ARM/x86
  - `docker-compose.yml` - Production-ready compose file
  - `casaos-config.json` - CasaOS App Store format
  - `.dockerignore` - Build optimization
- ✅ **Health checks** & auto-restart
- 📊 **Volume management** untuk data persistence
- 🔒 **Environment variable** support via .env

### Changed
- Updated `README.md` dengan Docker deployment section
- Improved documentation structure

### Deployment Methods
1. **CasaOS UI** - Import via App Store
2. **Docker Compose** - Manual deployment
3. **Setup Scripts** - Automated setup

## [1.0.0] - 2026-02-08

### Added
- 🏪 Core POS system features
- 👤 User authentication (Admin & Kasir)
- 📦 Product & inventory management
- 💰 Transaction processing & receipt
- 💳 Member management
- 📊 Reports & analytics
- 💾 Automatic backup system
- 💵 **Harga Variasi (Tier Pricing)** - Multiple price based on quantity
- 📱 **Telegram Bot Integration**:
  - Remote monitoring
  - Real-time reports
  - Low stock alerts
  - Transaction notifications
  - Sales charts

### Technical Stack
- Flask 3.0.3
- SQLite database
- SQLAlchemy ORM
- Bootstrap 5 UI
- Python Telegram Bot 20.8

### Security Features
- Password hashing
- CSRF protection
- Role-based access control
- Session management

---

## Deployment Platforms

### Supported
✅ Windows (native Python)
✅ Linux (native Python)
✅ Docker (any platform)
✅ CasaOS (STB/NAS)
✅ ARM devices (STB HG680P, Raspberry Pi)

### Tested On
- Windows 10/11
- Ubuntu 20.04+
- CasaOS 0.4.4+
- STB HG680P (Amlogic S905X)
- Docker 20.10+
- Docker Compose 1.29+

---

## Version Scheme

Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes atau architecture changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, minor improvements
