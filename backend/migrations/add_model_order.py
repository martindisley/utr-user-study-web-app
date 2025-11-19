"""
Migration script to add model_order column to users table
Run this once to update existing database schema.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session
from sqlalchemy import text
import random
from config import AVAILABLE_MODELS


def assign_model_order():
    """Generate a randomized model order for counterbalancing."""
    model_ids = [m['id'] for m in AVAILABLE_MODELS]
    random.shuffle(model_ids)
    return ','.join(model_ids)


def migrate():
    """Add model_order column and populate for existing users."""
    db = get_db_session()
    
    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        
        if 'model_order' in columns:
            print("Column 'model_order' already exists. Migration not needed.")
            return
        
        # Add the column
        print("Adding model_order column to users table...")
        db.execute(text("ALTER TABLE users ADD COLUMN model_order VARCHAR(100)"))
        db.commit()
        print("Column added successfully.")
        
        # Update existing users with random model orders
        result = db.execute(text("SELECT id FROM users WHERE model_order IS NULL"))
        user_ids = [row[0] for row in result]
        
        if user_ids:
            print(f"Assigning model orders to {len(user_ids)} existing users...")
            for user_id in user_ids:
                order = assign_model_order()
                db.execute(
                    text("UPDATE users SET model_order = :order WHERE id = :id"),
                    {"order": order, "id": user_id}
                )
            db.commit()
            print(f"Successfully assigned model orders to {len(user_ids)} users.")
        else:
            print("No existing users to update.")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    migrate()
