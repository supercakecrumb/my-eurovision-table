import os
import sys
from flask import Flask
from app import create_app
from app.models import db, Stage, Country, StageCountry

def migrate_database():
    """
    Migrate from the old association_table to the new StageCountry model
    This script should be run once after updating the models.py file
    """
    print("\n🔄 Migrating database to use StageCountry model")
    print("===============================================")
    
    # Create a temporary table to store existing associations
    print("1️⃣ Extracting existing stage-country associations...")
    
    # Get all existing associations
    existing_associations = []
    try:
        # Try to query the old association table directly
        result = db.session.execute("SELECT stage_id, country_id FROM association")
        for row in result:
            existing_associations.append((row[0], row[1]))
        print(f"✅ Found {len(existing_associations)} existing associations")
    except Exception as e:
        print(f"❌ Error accessing old association table: {str(e)}")
        print("⚠️ This might be because the migration was already performed")
        print("⚠️ Checking if StageCountry table exists and has data...")
        
        # Check if StageCountry table exists and has data
        try:
            count = StageCountry.query.count()
            if count > 0:
                print(f"✅ StageCountry table exists and has {count} records")
                print("✅ Migration appears to be already complete")
                return
            else:
                print("⚠️ StageCountry table exists but is empty")
                print("⚠️ Will attempt to recreate associations from Stage and Country relationships")
                
                # Try to get associations from the Stage.countries relationship
                stages = Stage.query.all()
                for stage in stages:
                    for country in stage.countries:
                        existing_associations.append((stage.id, country.id))
                
                if existing_associations:
                    print(f"✅ Recovered {len(existing_associations)} associations from relationships")
                else:
                    print("❌ Could not recover any associations")
                    print("❌ Migration failed - please check your database")
                    return
        except Exception as e:
            print(f"❌ Error checking StageCountry table: {str(e)}")
            print("❌ Migration failed - please check your database")
            return
    
    # Create new StageCountry records with order
    print("2️⃣ Creating new StageCountry records with order...")
    
    # Clear any existing StageCountry records
    StageCountry.query.delete()
    db.session.commit()
    
    # Add new records with order based on the sequence in the association table
    stage_counters = {}  # To keep track of order for each stage
    
    for stage_id, country_id in existing_associations:
        # Get the next order number for this stage
        if stage_id not in stage_counters:
            stage_counters[stage_id] = 1
        else:
            stage_counters[stage_id] += 1
        
        # Create new StageCountry record
        stage_country = StageCountry(
            stage_id=stage_id,
            country_id=country_id,
            order=stage_counters[stage_id]
        )
        db.session.add(stage_country)
    
    db.session.commit()
    print(f"✅ Created {len(existing_associations)} new StageCountry records with order")
    
    # Verify the migration
    print("3️⃣ Verifying migration...")
    count = StageCountry.query.count()
    if count == len(existing_associations):
        print(f"✅ Verification successful: {count} records in StageCountry table")
    else:
        print(f"⚠️ Verification warning: Expected {len(existing_associations)} records, found {count}")
    
    print("\n✅ Migration complete!")
    print("✅ You can now use the StageCountry model with order")
    print("✅ The old association table will be dropped when you restart the application")

if __name__ == "__main__":
    # Create app context
    app = create_app()
    
    with app.app_context():
        migrate_database()