# 🔧 Setup Guide - Kasir Toko Sembako

Panduan lengkap setup aplikasi dari awal.

## Prerequisites

- **Python 3.10.11** atau lebih baru
- **Windows 7/10/11** (untuk `.bat` scripts)
- Minimal 200MB free disk space
- Administrator access (optional)

## Step-by-Step Installation

### 1. Clone/Download Project
```bash
cd d:\python
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows CMD:**
```bash
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

Packages:
- Flask==3.0.3
- Flask-SQLAlchemy==3.1.1
- Flask-Login==0.6.3
- Flask-WTF==1.2.1
- WTForms==3.1.2
- werkzeug==3.0.4

### 5. Run Application

**Option A: Double-click (Recommended)**
```
scripts/start_app.bat
```

**Option B: Command Line**
```bash
python app_simple.py
```

### 6. Access Application
```
Local:    http://localhost:5000
Network:  http://192.168.x.x:5000
```

## Initial Login

```
Admin User:
- Username: admin
- Password: admin123

Kasir User:
- Username: kasir
- Password: kasir123
```

## Configuration

Edit `app_simple.py` untuk:

```python
# Port
app.run(port=5000)  # Ganti dengan port lain jika needed

# Debug mode
app.run(debug=True)  # Set False untuk production

# Host binding
app.run(host='0.0.0.0')  # Untuk network access

# Secret key
app.config['SECRET_KEY'] = 'your-secret-key'
```

## Database

SQLite database auto-created di `instance/kasir.db` dengan:
- 2 default users (admin & kasir)
- 5 sample categories
- 5 sample products

### Reset Database
1. Delete `instance/kasir.db`
2. Restart aplikasi
3. Database recreated with sample data

## Backup Management

Launch menu:
```bash
scripts/backup_manage.bat
```

Options:
1. **List Backups**: View all backup files
2. **Restore Latest**: Restore dari backup terbaru
3. **Backup Now**: Manual backup
4. **Cleanup**: Hapus backup lama, keep 5 terbaru
5. **Open Folder**: Open backups folder di Explorer

Auto-backup terjadi setelah setiap transaksi.

## Network Access

### Dari Device Lain (HP/Laptop)

1. **Get IP Address** (dari PC yang jalankan app):
```bash
ipconfig
```
Cari "IPv4 Address", contoh: `192.168.1.24`

2. **Dari device lain**, buka browser:
```
http://192.168.1.24:5000
```

### Requirements:
- Same network (WiFi/LAN)
- Port 5000 not blocked by firewall
- Both devices online

## Firewall Configuration

Jika tidak bisa akses dari device lain:

**Windows Firewall:**
1. Control Panel → Windows Defender Firewall
2. Advanced Settings → Inbound Rules
3. New Rule → Port → TCP → 5000
4. Allow connection → Apply

Atau disable firewall for testing:
```powershell
# PowerShell as Admin
netsh advfirewall set allprofiles state off
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID with actual number)
taskkill /PID 12345 /F
```

### Virtual Environment Issues
```bash
# Deactivate current venv
deactivate

# Delete and recreate
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Module Not Found
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt

# Or specific package
pip install Flask==3.0.3 -U
```

### Database Error
```bash
# Reset database
del instance\kasir.db

# Restart app - will recreate
python app_simple.py
```

### Can't Connect from Network

1. Check PC IP: `ipconfig`
2. Check firewall port: `netstat -ano | findstr :5000`
3. Disable firewall temporarily for testing
4. Ensure same network (WiFi/LAN)

## Performance Tips

- Use SSD for faster database operations
- Close unnecessary browser tabs
- Regular database cleanup (delete old transactions)
- Backup dikeep max 10 files

## Production Deployment

Untuk production, gunakan proper WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_simple:app
```

## Maintenance

### Weekly
- Check backup folder size
- Review transaction data

### Monthly
- Backup important data
- Update reports
- Check stock levels

### Quarterly
- Database optimization
- Update Python/packages if needed

---

**Questions?** Check README.md di root folder.
