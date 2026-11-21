# SchemeSathi AI — Database Persistence, Backup & Lifecycle Strategy

## 1. Executive Summary & Infrastructure Overview

SchemeSathi AI operates on a multi-tier cloud deployment:
- **Frontend**: React + TypeScript + Vite hosted on Vercel.
- **Backend**: FastAPI web service hosted on Render.
- **Primary Database**: Render-managed PostgreSQL.
- **Local Fallback**: SQLite (`sqlite:///./schemesathi.db`) for isolated local development and deterministic unit testing.

This document establishes the official database lifecycle policy, automated vs manual backup protocols, disaster recovery procedures, and a cost-conscious managed database comparison.

---

## 2. Current Render PostgreSQL Free Tier Analysis

### 2.1 Technical Specifications & Plan Limits
- **Plan**: Render Free PostgreSQL
- **Storage**: 1 GB maximum capacity
- **Connections**: Up to 97 concurrent connections
- **RAM / CPU**: Shared vCPU with ephemeral memory limits
- **Persistence Window**: **30 Days Maximum Lifetime**

### 2.2 Critical Expiration & Data Loss Implications
> [!WARNING]
> Render Free PostgreSQL databases automatically expire and are **permanently deleted after 30 days** from creation. 
> Render does **NOT** provide automated daily snapshots or Point-in-Time Recovery (PITR) on free-tier databases. If a free-tier database expires without an active upgrade or external backup, all persisted citizen profiles, document metadata, and checklist progress are unrecoverable.

---

## 3. Standard Operating Procedures (SOP): Backup & Recovery

### 3.1 Prerequisites
Ensure `postgresql-client` tools (`pg_dump`, `pg_restore`) are available on the administrative workstation.

### 3.2 Secure Manual Backup Procedure (`pg_dump`)

To take an encrypted, compressed binary snapshot of the production PostgreSQL database:

```bash
# 1. Retrieve the External Database URL from Render Dashboard (or .env.production)
# Format: postgresql://[user]:[password]@[host]:[port]/[database]

# 2. Run pg_dump in Custom Format (-Fc for maximum compression and flexible restore)
pg_dump "$DATABASE_URL" \
  --format=custom \
  --blobs \
  --verbose \
  --file="schemesathi_prod_backup_$(date +%Y%m%d_%H%M%S).dump"
```

To create a human-readable SQL schema and data export:
```bash
pg_dump "$DATABASE_URL" \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --file="schemesathi_prod_backup_$(date +%Y%m%d_%H%M%S).sql"
```

### 3.3 Safe Disaster Recovery & Restore Procedure (`pg_restore`)

> [!CAUTION]
> Never execute restore operations on a live production database during active citizen traffic without scheduling a maintenance window.

To restore a custom-format dump into a newly provisioned PostgreSQL instance:

```bash
# 1. Set target database URL
export TARGET_DB_URL="postgresql://[new_user]:[new_password]@[new_host]:[port]/[new_database]"

# 2. Execute pg_restore with clean recreate flag
pg_restore \
  --dbname="$TARGET_DB_URL" \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --verbose \
  "schemesathi_prod_backup_YYYYMMDD_HHMMSS.dump"

# 3. Verify database table integrity
psql "$TARGET_DB_URL" -c "SELECT count(*) FROM government_schemes;"
psql "$TARGET_DB_URL" -c "SELECT count(*) FROM scholarships;"
psql "$TARGET_DB_URL" -c "SELECT count(*) FROM official_sources;"
```

---

## 4. Cost-Conscious Production Database Comparison

To eliminate the 30-day free tier expiration while keeping operational costs minimal for hackathon and initial deployment:

| Provider | Plan | Monthly Cost | Storage | Backups & Retention | Standby / Sleep Behavior | Recommendation |
|---|---|---:|---|---|---|---|
| **Render PostgreSQL** | Starter | \$7 / mo | 10 GB SSD | Automated daily backups, 7-day retention | Always-on, 0 latency, same datacenter as backend | **Recommended for Production**: Zero configuration changes needed in `render.yaml`. |
| **Neon Serverless** | Free Tier | \$0 / mo | 0.5 GB | Point-in-time branching (History retention) | Scales to zero on inactivity (~500ms cold start) | **Best Free Alternative**: No 30-day auto-deletion. Excellent developer branching. |
| **Supabase** | Free Tier | \$0 / mo | 500 MB | Daily backups | Pauses after 7 days of zero activity | Viable, but requires wake-up ping to prevent pausing. |

### Architectural Recommendation
1. **Immediate Hackathon Stage**: Keep Render PostgreSQL or migrate connection string to Neon Free Tier to avoid the 30-day deletion cutoff without recurring costs.
2. **Public Launch Stage**: Upgrade Render PostgreSQL to Starter ($7/month), placing database and backend compute within the same Frankfurt or Oregon region for sub-2ms network roundtrips.

---

## 5. Schema Migration & Idempotency Rules

1. **Additive Changes Only**:
   - Columns must be added with default values or as nullable (`nullable=True`).
   - Destructive commands (`DROP TABLE`, `ALTER TABLE ... DROP COLUMN`) are strictly forbidden in automated startup scripts.
2. **Safe Idempotent Initialization**:
   - `backend/app/database.py:init_db()` checks table presence before running `Base.metadata.create_all(bind=engine)`.
   - Seeding routines (`backend/app/data/seed_db.py`) query existing primary keys (`id`) and perform updates or skips, preventing duplicate row errors on container restarts.
3. **Application Decoupling**:
   - Health checks distinguish between liveness (`/api/health`) and database readiness (`/api/ready`) to prevent cascading container crashes during brief database maintenance or reboots.
