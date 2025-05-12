from decouple import config
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

print("Starting database migration...")

# Connect to the database
engine = create_engine(config("DATABASE_URL"))
connection = engine.connect()

# Add new columns to Entry table
try:
    print("Adding description column to Entry table...")
    connection.execute(text("ALTER TABLE entry ADD COLUMN IF NOT EXISTS description TEXT;"))
    
    print("Adding body column to Entry table...")
    connection.execute(text("ALTER TABLE entry ADD COLUMN IF NOT EXISTS body TEXT;"))
    
    print("Adding tags column to Entry table...")
    connection.execute(text("ALTER TABLE entry ADD COLUMN IF NOT EXISTS tags JSONB;"))
    
    connection.commit()
    print("Migration completed successfully!")
except Exception as e:
    print(f"Error during migration: {e}")
finally:
    connection.close() 