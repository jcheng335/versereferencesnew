# PostgreSQL Database Import Instructions

## Overview
The SQLite database has been exported to `bible_data.sql` containing:
- 66 books
- 31,103 verses with full Bible text
- 270 book abbreviations

## Step-by-Step Import Process

### Step 1: Get Your Database Credentials
1. Go to your Render PostgreSQL dashboard: https://dashboard.render.com/d/dpg-d2lsvpn5r7bs73e32s40-a
2. Click the **"Connect"** button
3. Copy the **"External Database URL"** (starts with `postgresql://`)

### Step 2: Import Using Command Line

#### Option A: Using psql (Recommended)
```bash
# If you have PostgreSQL installed locally:
psql "YOUR_EXTERNAL_DATABASE_URL" < bible_data.sql
```

#### Option B: Using pg_restore
```bash
# Alternative method
cat bible_data.sql | psql "YOUR_EXTERNAL_DATABASE_URL"
```

### Step 3: Verify the Import
After import, verify the data:

```bash
# Check verse count (should be 31103)
psql "YOUR_EXTERNAL_DATABASE_URL" -c "SELECT COUNT(*) FROM verses;"

# Check books count (should be 66)
psql "YOUR_EXTERNAL_DATABASE_URL" -c "SELECT COUNT(*) FROM books;"

# Test a sample verse
psql "YOUR_EXTERNAL_DATABASE_URL" -c "SELECT text FROM verses v JOIN books b ON v.book_id = b.id WHERE b.name = 'Ephesians' AND v.chapter = 4 AND v.verse = 7;"
```

### Step 4: Using Render's Web Interface (Alternative)
If you don't have psql installed:

1. Go to https://dashboard.render.com/d/dpg-d2lsvpn5r7bs73e32s40-a
2. Click **"Connect"** → **"PSQL Command"**
3. This opens a web terminal
4. Copy and paste the contents of `bible_data.sql` in smaller chunks:
   - First paste the table creation commands
   - Then paste the book inserts
   - Then paste verses in batches (about 100 at a time)
   - Finally paste the abbreviations

### Step 5: Configure Your Application
Once imported, ensure your application has the DATABASE_URL environment variable set in Render:

1. Go to your backend service: https://dashboard.render.com/web/srv-d2ltokje5dus7396ijh0
2. Click **"Environment"**
3. Add/Update: `DATABASE_URL` with your Internal Database URL

## Troubleshooting

### If psql is not installed:
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **Mac**: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql-client`

### Connection Issues:
If the DATABASE_URL doesn't work directly, use individual parameters:
```bash
psql -h oregon-postgres.render.com -p 5432 -U bible_outline_user -d bible_outline_db < bible_data.sql
```

### Large File Issues:
If the import times out, split the SQL file:
```bash
# Split into smaller files
split -l 1000 bible_data.sql bible_part_

# Import each part
for file in bible_part_*; do
    psql "YOUR_DATABASE_URL" < $file
done
```

## Expected Results
After successful import:
- `books` table: 66 records
- `verses` table: 31,103 records  
- `book_abbreviations` table: 270 records

All verses will contain full Bible text, not just references.

## Files Created
- `bible_data.sql` - Complete SQL dump (6.6 MB)
- `direct_postgres_import.py` - Python import script (if you prefer Python)
- `migrate_to_postgresql.py` - Alternative migration script