import sqlite3
import pandas as pd

conn = sqlite3.connect('db/crm.db')

# Create database
pd.read_csv('db/seeds/accounts_raw.csv').to_sql('accounts', conn, if_exists='replace')
pd.read_csv('db/seeds/users_raw.csv').to_sql('users', conn, if_exists='replace')
pd.read_csv('db/seeds/deals_raw.csv').to_sql('deals', conn, if_exists='replace')
pd.read_csv('db/seeds/tracks_raw.csv').to_sql('tracks', conn, if_exists='replace')
pd.read_csv('db/seeds/addresses_raw.csv').to_sql('addresses', conn, if_exists='replace')
pd.read_csv('db/seeds/countries_raw.csv').to_sql('countries', conn, if_exists='replace')
pd.read_csv('db/seeds/sales_targets_raw.csv').to_sql('sales_target', conn, if_exists='replace')
pd.read_csv('db/seeds/user_deals_raw.csv').to_sql('user_deals', conn, if_exists='replace')

print(pd.read_sql("SELECT COUNT(*) FROM accounts", conn))

# Verify data structure
# List all tables
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print("=== TABLES IN DATABASE ===")
print(tables)
print("\n")

# Explore each table
for table in ['accounts', 'users', 'deals', 'tracks', 'addresses', 'countries', 'sales_target', 'user_deals']:
    try:
        # Get column info
        columns = pd.read_sql(f"PRAGMA table_info({table})", conn)
        print(f"=== {table.upper()} TABLE ===")
        print(f"Columns: {list(columns['name'])}")
        
        # Get sample data
        sample = pd.read_sql(f"SELECT * FROM {table} LIMIT 3", conn)
        print(f"Sample data:\n{sample}")
        print(f"Total rows: {pd.read_sql(f'SELECT COUNT(*) FROM {table}', conn).iloc[0, 0]}")
        print("\n")
    except Exception as e:
        print(f"Error with {table}: {e}")

# Create normalized tables with relationships
conn.executescript('''
    -- Drop old tables if they exist
    DROP TABLE IF EXISTS tracks_normalized;
    DROP TABLE IF EXISTS user_deals_normalized;
    DROP TABLE IF EXISTS addresses_normalized;
    DROP TABLE IF EXISTS deals_normalized;
    DROP TABLE IF EXISTS users_normalized;
    DROP TABLE IF EXISTS accounts_normalized;
    DROP TABLE IF EXISTS countries_normalized;
    DROP TABLE IF EXISTS sales_target_normalized;
    
    -- Create accounts table with proper schema
    CREATE TABLE accounts_normalized (
        account_id TEXT PRIMARY KEY,
        account_name TEXT,
        industry TEXT,
        segment TEXT
    );
    
    -- Create users table with foreign key
    CREATE TABLE users_normalized (
        user_id TEXT PRIMARY KEY,
        account_id TEXT NOT NULL,
        email TEXT,
        job_title TEXT,
        is_marketing_opted_in BOOLEAN,
        created_at DATETIME, 
        first_logged_in_at DATETIME, 
        latest_logged_in_at DATETIME,
        FOREIGN KEY (account_id) REFERENCES accounts_normalized(account_id)
    );
    
    -- Create deals table with foreign key
    CREATE TABLE deals_normalized (
        deal_id TEXT PRIMARY KEY,
        account_id TEXT NOT NULL,
        stage TEXT,
        plan TEXT,
        seats INTEGER,
        amount INTEGER,
        created_date DATETIME,
        FOREIGN KEY (account_id) REFERENCES accounts_normalized(account_id)
    );
    
    -- Create tracks table with foreign key
    CREATE TABLE tracks_normalized (
        track_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        event_id TEXT,
        event_name TEXT,
        event_timestamp DATETIME,
        FOREIGN KEY (user_id) REFERENCES users_normalized(user_id)
    );
    
    -- Create countries table
    CREATE TABLE countries_normalized (
        iso_code TEXT PRIMARY KEY,
        country_name TEXT
    );
    
    -- Create addresses table with foreign key
    CREATE TABLE addresses_normalized (
        address_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        street_address TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        country_iso_code TEXT,
        valid_from DATETIME,
        valid_to DATETIME,
        FOREIGN KEY (user_id) REFERENCES users_normalized(user_id),
        FOREIGN KEY (country_iso_code) REFERENCES countries_normalized(iso_code)
    );
    
    -- Create sales_target table
    CREATE TABLE sales_target_normalized (
        sales_target_id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type TEXT,
        target_value TEXT,
        quarter_start_date DATE,
        target_deals INTEGER,
        target_amount INTEGER
    );
    
    -- Create user_deals table with foreign key
    CREATE TABLE user_deals_normalized (
        user_deals_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        deal_id TEXT NOT NULL,
        role TEXT,
        FOREIGN KEY (user_id) REFERENCES users_normalized(user_id),
        FOREIGN KEY (deal_id) REFERENCES deals_normalized(deal_id)
    );
    -- =====================================================
    -- CREATE INDEXES FOR PERFORMANCE
    -- =====================================================

    -- Accounts indexes
    CREATE INDEX IF NOT EXISTS idx_accounts_industry ON accounts_normalized(industry);
    CREATE INDEX IF NOT EXISTS idx_accounts_segment ON accounts_normalized(segment);

    -- Users indexes
    CREATE INDEX IF NOT EXISTS idx_users_account ON users_normalized(account_id);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users_normalized(email);
    CREATE INDEX IF NOT EXISTS idx_users_last_login ON users_normalized(latest_logged_in_at);

    -- Deals indexes
    CREATE INDEX IF NOT EXISTS idx_deals_account ON deals_normalized(account_id);
    CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals_normalized(stage);
    CREATE INDEX IF NOT EXISTS idx_deals_created ON deals_normalized(created_date);

    -- Tracks indexes
    CREATE INDEX IF NOT EXISTS idx_tracks_user ON tracks_normalized(user_id);
    CREATE INDEX IF NOT EXISTS idx_tracks_timestamp ON tracks_normalized(event_timestamp);
    CREATE INDEX IF NOT EXISTS idx_tracks_event ON tracks_normalized(event_name);

    -- Addresses indexes
    CREATE INDEX IF NOT EXISTS idx_addresses_user ON addresses_normalized(user_id);
    CREATE INDEX IF NOT EXISTS idx_addresses_country ON addresses_normalized(country_iso_code);

    -- User_Deals indexes
    CREATE INDEX IF NOT EXISTS idx_user_deals_user ON user_deals_normalized(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_deals_deal ON user_deals_normalized(deal_id);
'''
)

# Migrate data from raw tables
conn.execute("""
    INSERT INTO accounts_normalized (account_id, account_name, industry, segment)
    SELECT account_id, account_name, industry, segment FROM accounts
""")

conn.execute("""
    INSERT INTO users_normalized (user_id, account_id, email, job_title, is_marketing_opted_in, created_at, first_logged_in_at, latest_logged_in_at)
    SELECT user_id, account_id, email, job_title, is_marketing_opted_in, created_at, first_logged_in_at, latest_logged_in_at FROM users
""")

conn.execute("""
    INSERT INTO deals_normalized (deal_id, account_id, stage, plan, seats, amount, created_date)
    SELECT deal_id, account_id, stage, plan, seats, amount, created_date FROM deals
""")

conn.execute("""
    INSERT INTO tracks_normalized (user_id, event_id, event_name, event_timestamp)
    SELECT user_id, event_id, event_name, event_timestamp FROM tracks
""")

conn.execute("""
    INSERT INTO countries_normalized (iso_code, country_name)
    SELECT iso_code, country_name FROM countries
""")

conn.execute("""
    INSERT INTO addresses_normalized (address_id, user_id, street_address, city, state, postal_code, country_iso_code, valid_from, valid_to)
    SELECT address_id, user_id, street_address, city, state, postal_code, country_iso_code, valid_from, valid_to FROM addresses
""")

conn.execute("""
    INSERT INTO sales_target_normalized (target_type, target_value, quarter_start_date, target_deals, target_amount)
    SELECT target_type, target_value, quarter_start_date, target_deals, target_amount FROM sales_target
""")

conn.execute("""
    INSERT INTO user_deals_normalized (user_id, deal_id, role)
    SELECT user_id, deal_id, role FROM user_deals
""")

print("✅ Schema setup complete!")
print(f"Accounts: {conn.execute('SELECT COUNT(*) FROM accounts_normalized').fetchone()[0]}")
print(f"Users: {conn.execute('SELECT COUNT(*) FROM users_normalized').fetchone()[0]}")
print(f"Deals: {conn.execute('SELECT COUNT(*) FROM deals_normalized').fetchone()[0]}")
print(f"Tracks: {conn.execute('SELECT COUNT(*) FROM tracks_normalized').fetchone()[0]}")
print(f"Addresses: {conn.execute('SELECT COUNT(*) FROM addresses_normalized').fetchone()[0]}")
print(f"Countries: {conn.execute('SELECT COUNT(*) FROM countries_normalized').fetchone()[0]}")
print(f"Sales_target: {conn.execute('SELECT COUNT(*) FROM sales_target_normalized').fetchone()[0]}")
print(f"User_deals: {conn.execute('SELECT COUNT(*) FROM user_deals_normalized').fetchone()[0]}")

conn.close()