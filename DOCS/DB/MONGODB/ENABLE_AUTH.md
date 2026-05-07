# Enable MongoDB Authentication

## Current Issue

You're getting `Authentication failed` because your `.env` has MongoDB credentials but MongoDB doesn't have authentication enabled by default.

## Quick Fix (Development)

**Remove credentials from `.env`:**

```env
MONGODB_USER=
MONGODB_PASSWORD=
```

This will connect without authentication (fine for local development).

---

## Option 2: Enable MongoDB Authentication (Production)

If you want to enable authentication:

### Step 1: Connect to MongoDB Without Auth

```bash
mongosh
```

### Step 2: Switch to Admin Database

```javascript
use admin
```

### Step 3: Create Admin User

```javascript
db.createUser({
  user: "admin",
  pwd: "your_secure_password",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
});
```

### Step 4: Create Application User

```javascript
use sentinel_health

db.createUser({
  user: "sentinel_app",
  pwd: "your_app_password",
  roles: [
    { role: "readWrite", db: "sentinel_health" }
  ]
});
```

### Step 5: Enable Authentication

**Windows:**

Edit `C:\Program Files\MongoDB\Server\6.0\bin\mongod.cfg`:

```yaml
security:
  authorization: enabled
```

**macOS (Homebrew):**

Edit `/opt/homebrew/etc/mongod.conf`:

```yaml
security:
  authorization: enabled
```

**Linux:**

Edit `/etc/mongod.conf`:

```yaml
security:
  authorization: enabled
```

### Step 6: Restart MongoDB

**Windows:**
```bash
net stop MongoDB
net start MongoDB
```

**macOS:**
```bash
brew services restart mongodb-community
```

**Linux:**
```bash
sudo systemctl restart mongod
```

### Step 7: Update `.env`

```env
MONGODB_USER=sentinel_app
MONGODB_PASSWORD=your_app_password
```

### Step 8: Test Connection

```bash
mongosh "mongodb://sentinel_app:your_app_password@localhost:27017/sentinel_health"
```

---

## Verify Connection from FastAPI

Restart your FastAPI server:

```bash
uvicorn app.main:app --reload
```

Check health endpoint:

```bash
curl http://localhost:8000/api/v1/health/mongodb
```

Expected response:
```json
{
  "status": "healthy",
  "database": "mongodb",
  "host": "localhost",
  "port": 27017,
  "database_name": "sentinel_health",
  "collections_count": 5,
  "response_time_ms": 12.34
}
```

---

## Troubleshooting

### Still Getting Authentication Failed?

1. **Check if auth is actually enabled:**
   ```bash
   mongosh --eval "db.adminCommand({ getCmdLineOpts: 1 })"
   ```

2. **Verify user exists:**
   ```bash
   mongosh admin -u admin -p your_secure_password --eval "db.getUsers()"
   ```

3. **Check connection string:**
   ```bash
   # Should work
   mongosh "mongodb://sentinel_app:password@localhost:27017/sentinel_health"
   ```

### Connection Timeout?

Check if MongoDB is running:

```bash
# Windows
sc query MongoDB

# macOS
brew services list | grep mongodb

# Linux
sudo systemctl status mongod
```

### Wrong Database Name?

Make sure database name matches in:
- `.env` → `MONGODB_DB=sentinel_health`
- MongoDB user creation → `use sentinel_health`
- Connection test

---

## Recommended Setup

**Development (Local):**
- ✅ No authentication (simpler)
- ✅ Faster iteration

**Production:**
- ✅ Enable authentication
- ✅ Use strong passwords
- ✅ Restrict network access
- ✅ Enable SSL/TLS
- ✅ Regular backups

---

**Last Updated**: May 6, 2026
