# Database Migration Guide

## Overview

After the initial schema is locked, all database changes must be done through migrations to maintain consistency across environments.

---

## PostgreSQL Migrations (Alembic)

### Setup

Alembic is already configured in `Backend/alembic/`.

### Creating Migrations

#### Manual Migration

```bash
cd Backend
alembic revision -m "add_new_column_to_users"
```

This creates a new file in `alembic/versions/`.

Edit the file:

```python
def upgrade() -> None:
    op.add_column('users', 
        sa.Column('phone_number', sa.String(20), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

#### Auto-Generate Migration (from SQLAlchemy models)

```bash
alembic revision --autogenerate -m "add_phone_to_users"
```

**Note**: Always review auto-generated migrations before applying!

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Checking Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

---

## MongoDB Migrations

MongoDB doesn't have a built-in migration system, but we can use a custom approach.

### Creating MongoDB Migrations

Create migration files in `Backend/migrations/mongodb/`:

```javascript
// Backend/migrations/mongodb/001_add_field_to_analyzed_posts.js

// Migration: Add new field to analyzed_posts
// Date: 2026-05-07

db.analyzed_posts.updateMany(
  { multimodal_analysis: { $exists: false } },
  { 
    $set: { 
      multimodal_analysis: {
        images_analyzed: false,
        videos_analyzed: false,
        analysis_results: []
      }
    }
  }
);

print("✓ Added multimodal_analysis field to analyzed_posts");
```

### Applying MongoDB Migrations

```bash
mongosh sentinel_health < Backend/migrations/mongodb/001_add_field_to_analyzed_posts.js
```

### MongoDB Migration Best Practices

1. **Always use `updateMany` with filters** to avoid updating all documents
2. **Check if field exists** before adding: `{ field: { $exists: false } }`
3. **Test on development first**
4. **Keep migrations idempotent** (can run multiple times safely)
5. **Document the migration** with comments

---

## Migration Workflow

### 1. Development

```bash
# Make schema changes
# Create migration
alembic revision -m "description"

# Edit migration file
# Apply migration
alembic upgrade head

# Test thoroughly
```

### 2. Version Control

```bash
git add alembic/versions/
git commit -m "Add migration: description"
git push
```

### 3. Staging/Production

```bash
# Pull latest code
git pull

# Review pending migrations
alembic history

# Backup database first!
pg_dump sentinel_health > backup_$(date +%Y%m%d).sql

# Apply migrations
alembic upgrade head

# Verify
alembic current
```

---

## Common Migration Patterns

### Add Column

```python
def upgrade():
    op.add_column('table_name',
        sa.Column('new_column', sa.String(255), nullable=True)
    )

def downgrade():
    op.drop_column('table_name', 'new_column')
```

### Modify Column

```python
def upgrade():
    op.alter_column('table_name', 'column_name',
        type_=sa.String(500),
        existing_type=sa.String(255)
    )

def downgrade():
    op.alter_column('table_name', 'column_name',
        type_=sa.String(255),
        existing_type=sa.String(500)
    )
```

### Add Index

```python
def upgrade():
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email', 'users')
```

### Add Foreign Key

```python
def upgrade():
    op.create_foreign_key(
        'fk_posts_user_id',
        'posts', 'users',
        ['user_id'], ['id']
    )

def downgrade():
    op.drop_constraint('fk_posts_user_id', 'posts')
```

### Rename Column

```python
def upgrade():
    op.alter_column('table_name', 'old_name',
        new_column_name='new_name'
    )

def downgrade():
    op.alter_column('table_name', 'new_name',
        new_column_name='old_name'
    )
```

### Add Enum Type

```python
from sqlalchemy.dialects.postgresql import ENUM

def upgrade():
    status_enum = ENUM('active', 'inactive', 'pending',
        name='status_enum', create_type=False)
    status_enum.create(op.get_bind(), checkfirst=True)
    
    op.add_column('table_name',
        sa.Column('status', status_enum, nullable=False)
    )

def downgrade():
    op.drop_column('table_name', 'status')
    ENUM(name='status_enum').drop(op.get_bind(), checkfirst=True)
```

---

## MongoDB Migration Patterns

### Add Field to All Documents

```javascript
db.collection_name.updateMany(
  { new_field: { $exists: false } },
  { $set: { new_field: default_value } }
);
```

### Rename Field

```javascript
db.collection_name.updateMany(
  {},
  { $rename: { "old_field": "new_field" } }
);
```

### Remove Field

```javascript
db.collection_name.updateMany(
  {},
  { $unset: { "field_to_remove": "" } }
);
```

### Change Field Type

```javascript
db.collection_name.find({ field: { $type: "string" } }).forEach(doc => {
  db.collection_name.updateOne(
    { _id: doc._id },
    { $set: { field: parseInt(doc.field) } }
  );
});
```

### Add Index

```javascript
db.collection_name.createIndex({ field_name: 1 });
```

### Drop Index

```javascript
db.collection_name.dropIndex("index_name");
```

---

## Rollback Strategy

### PostgreSQL

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### MongoDB

Create reverse migration:

```javascript
// 001_add_field_rollback.js
db.analyzed_posts.updateMany(
  {},
  { $unset: { multimodal_analysis: "" } }
);
```

---

## Testing Migrations

### Test Locally First

```bash
# Create test database
createdb sentinel_health_test

# Apply migrations
POSTGRES_DB=sentinel_health_test alembic upgrade head

# Test application
# Rollback
alembic downgrade base

# Drop test database
dropdb sentinel_health_test
```

### Verify Data Integrity

```sql
-- Check row counts
SELECT COUNT(*) FROM table_name;

-- Check for NULL values
SELECT COUNT(*) FROM table_name WHERE new_column IS NULL;

-- Verify constraints
SELECT * FROM information_schema.table_constraints 
WHERE table_name = 'table_name';
```

---

## Emergency Rollback

If a migration causes issues in production:

1. **Immediate rollback**:
   ```bash
   alembic downgrade -1
   ```

2. **Restore from backup** (if rollback fails):
   ```bash
   psql sentinel_health < backup_20260506.sql
   ```

3. **Fix migration** and reapply:
   ```bash
   # Edit migration file
   alembic upgrade head
   ```

---

## Migration Checklist

Before applying migrations to production:

- [ ] Tested on development environment
- [ ] Tested on staging environment
- [ ] Database backup created
- [ ] Downgrade script tested
- [ ] Team notified of maintenance window
- [ ] Monitoring in place
- [ ] Rollback plan documented

---

## Troubleshooting

### Alembic: "Can't locate revision"

```bash
# Reset alembic version table
alembic stamp head
```

### Alembic: "Target database is not up to date"

```bash
# Check current version
alembic current

# Show pending migrations
alembic history

# Apply missing migrations
alembic upgrade head
```

### MongoDB: Migration failed midway

```javascript
// Check how many documents were updated
db.collection_name.countDocuments({ new_field: { $exists: true } });

// Complete the migration
db.collection_name.updateMany(
  { new_field: { $exists: false } },
  { $set: { new_field: default_value } }
);
```

---

**Last Updated**: May 6, 2026
