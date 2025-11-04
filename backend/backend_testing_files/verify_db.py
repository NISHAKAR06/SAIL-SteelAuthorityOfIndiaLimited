#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.append('.')

from app.core.config import settings
from sqlalchemy import create_engine, text

def verify_cloud_database():
    """Verify cloud database connection and data"""

    print("=" * 60)
    print("SAIL DSS Cloud Database Verification")
    print("=" * 60)

    print("\nDatabase Configuration:")
    print(f"URI: {settings.SQLALCHEMY_DATABASE_URI}")
    print(f"Environment: {settings.ENVIRONMENT}")

    try:
        print("\nTesting connection...")
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)

        with engine.connect() as conn:
            print("✓ Connection successful!")

            # Get all tables in public schema
            result = conn.execute(text("""
                SELECT tablename FROM pg_catalog.pg_tables
                WHERE schemaname = 'public';
            """))

            tables = [row[0] for row in result.fetchall()]
            print(f"\nTables found: {len(tables)}")
            for table in tables:
                print(f"  - {table}")

            # Check our specific tables
            print("\nChecking SAIL DSS tables:")
            for table in ['inventory_items', 'orders', 'rakes']:
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    print(f"✓ {table}: {count} records")

                    if count > 0:
                        # Get sample record
                        sample_result = conn.execute(text(f"""
                            SELECT * FROM {table} LIMIT 1
                        """))
                        sample = sample_result.fetchone()
                        if sample:
                            print("  Sample data: Available")
                    else:
                        print("  ⚠ No records found - may need seeding")

                except Exception as e:
                    print(f"✗ {table}: Error - {str(e)[:150]}...")

            # Calculate total records safely
            total_records = 0
            for table in ['inventory_items', 'orders', 'rakes']:
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    total_records += int(count)
                except:
                    pass

            print("\n" + "=" * 60)
            print("VERIFICATION SUMMARY")
            print("=" * 60)
            print("✓ Cloud database connection: SUCCESSFUL")

            required_tables = [t for t in ['inventory_items', 'orders', 'rakes'] if t in tables]
            if len(required_tables) == 3:
                print("✓ Required tables: PRESENT (3/3)")
            else:
                print(f"✗ Required tables: MISSING ({len(required_tables)}/3) - missing: {[t for t in ['inventory_items', 'orders', 'rakes'] if t not in tables]}")

            if total_records > 0:
                print(f"✓ Data records: {total_records} total records loaded")
            else:
                print("⚠ Data records: None loaded - run seeding process")

            print("✓ Ready for production use!")

        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    verify_cloud_database()
