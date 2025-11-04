#!/usr/bin/env python3

import sys
import os
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Define models to match existing ones
class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_location = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    material_grade = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, default='tons')
    storage_location = Column(String, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(100), nullable=False)
    customer_id = Column(Integer, nullable=True)
    material = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), default='tons')
    status = Column(String(50), default='pending')
    priority = Column(String(20), default='normal')
    origin_plant = Column(String(100), nullable=False, default='Plant A')
    destination = Column(String(100), nullable=False)
    rate_per_ton = Column(Float, nullable=True)

class Rake(Base):
    __tablename__ = 'rakes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rake_number = Column(String(50), nullable=False, unique=True)
    origin_plant = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    status = Column(String(50), default='Available')
    capacity_tons = Column(Float, nullable=False, default=0.0)
    priority = Column(String(20), default='normal')
    current_location = Column(String(100), nullable=True)
    total_wagons = Column(Integer, nullable=False, default=0)

def seed_database():
    """Seed cloud database with CSV data"""

    print("=" * 60)
    print("SAIL DSS Cloud Database Seeding")
    print("=" * 60)

    try:
        print("\nConnecting to cloud database...")
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created")

        # Check current data
        with SessionLocal() as db:
            inventory_count = db.query(InventoryItem).count()
            orders_count = db.query(Order).count()
            rakes_count = db.query(Rake).count()

            print(f"\nCurrent data counts:")
            print(f"  Inventory items: {inventory_count}")
            print(f"  Orders: {orders_count}")
            print(f"  Rakes: {rakes_count}")

            total_before = inventory_count + orders_count + rakes_count
            print(f"  Total: {total_before} records")

            # Seed inventory if needed
            if inventory_count == 0:
                print("\n🌱 Seeding inventory from CSV...")
                try:
                    # Check if CSV file exists
                    csv_path = os.path.join(os.path.dirname(__file__), 'statics', 'production_inventory.csv')
                    if not os.path.exists(csv_path):
                        print(f"❌ CSV file not found: {csv_path}")
                        return False

                    inventory_df = pd.read_csv(csv_path)
                    print(f"  Loaded {len(inventory_df)} rows from CSV")

                    seeded_count = 0
                    for idx, row in inventory_df.iterrows():
                        try:
                            item = InventoryItem(
                                plant_location=str(row.get('plant_location', 'Plant A')).strip(),
                                product_name=str(row.get('product_name', 'Steel Product')).strip(),
                                material_grade=str(row.get('material_grade', 'Grade A')).strip(),
                                quantity=float(row.get('quantity', 1000)),
                                unit=str(row.get('unit', 'tons')).strip(),
                                storage_location=str(row.get('storage_location', 'Storage A')).strip()
                            )
                            db.add(item)
                            seeded_count += 1

                            # Commit in batches of 100
                            if seeded_count % 100 == 0:
                                db.commit()
                                print(f"  → Committed batch of 100 items ({seeded_count}/{len(inventory_df)})")

                        except Exception as e:
                            print(f"  ⚠️  Error with row {idx}: {str(e)[:100]}...")
                            continue

                    db.commit()  # Final commit
                    print(f"✓ Seeded {seeded_count} inventory items successfully")

                except Exception as e:
                    print(f"❌ Error seeding inventory: {e}")
                    db.rollback()
                    return False

            # Seed orders if needed
            if orders_count == 0:
                print("\n🌱 Seeding orders from CSV...")
                try:
                    csv_path = os.path.join(os.path.dirname(__file__), 'statics', 'customer_orders.csv')
                    if not os.path.exists(csv_path):
                        print(f"❌ CSV file not found: {csv_path}")
                        return False

                    orders_df = pd.read_csv(csv_path)
                    print(f"  Loaded {len(orders_df)} rows from CSV")

                    seeded_count = 0
                    for idx, row in orders_df.iterrows():
                        try:
                            order = Order(
                                customer_name=str(row.get('customer_name', 'Customer A')).strip()[:100],
                                customer_id=int(float(row.get('customer_id', 1001))) if pd.notna(row.get('customer_id')) and str(row.get('customer_id')).strip() else None,
                                material=str(row.get('material', row.get('product_name', 'Steel'))).strip()[:100],
                                quantity=float(row.get('quantity', 500)),
                                unit=str(row.get('unit', 'tons')).strip()[:20],
                                status='pending',
                                priority='normal',
                                origin_plant=str(row.get('origin_plant', 'Plant A')).strip()[:100],
                                destination=str(row.get('destination', 'Location A')).strip()[:100],
                                rate_per_ton=float(row.get('rate_per_ton', 1000)) if pd.notna(row.get('rate_per_ton')) and str(row.get('rate_per_ton')).strip() else None
                            )
                            db.add(order)
                            seeded_count += 1

                            # Commit in batches of 100
                            if seeded_count % 100 == 0:
                                db.commit()
                                print(f"  → Committed batch of 100 orders ({seeded_count}/{len(orders_df)})")

                        except Exception as e:
                            print(f"  ⚠️  Error with order row {idx}: {str(e)[:100]}...")
                            continue

                    db.commit()  # Final commit
                    print(f"✓ Seeded {seeded_count} orders successfully")

                except Exception as e:
                    print(f"❌ Error seeding orders: {e}")
                    db.rollback()
                    return False

            # Seed rakes if needed
            if rakes_count == 0:
                print("\n🌱 Seeding rakes from CSV...")
                try:
                    csv_path = os.path.join(os.path.dirname(__file__), 'statics', 'rake_wagon_details.csv')
                    if not os.path.exists(csv_path):
                        print(f"❌ CSV file not found: {csv_path}")
                        return False

                    rakes_df = pd.read_csv(csv_path)
                    print(f"  Loaded {len(rakes_df)} rows from CSV")

                    seeded_count = 0
                    for idx, row in rakes_df.iterrows():
                        try:
                            rake = Rake(
                                rake_number=str(row.get('rake_number', f'RK{1000 + idx}')).strip(),
                                origin_plant=str(row.get('origin_plant', 'Plant A')).strip() if 'origin_plant' in row else 'Plant A',
                                destination=str(row.get('destination', 'Location B')).strip() if 'destination' in row else 'Location B',
                                status=str(row.get('status', 'Available')).strip(),
                                capacity_tons=float(row.get('capacity_tons', 2000)) if 'capacity_tons' in row and pd.notna(row.get('capacity_tons')) and str(row.get('capacity_tons')).strip() else 2000,
                                priority='normal',
                                current_location=str(row.get('current_location', 'At Plant')).strip() if 'current_location' in row else 'At Plant',
                                total_wagons=int(row.get('total_wagons', 20)) if 'total_wagons' in row and pd.notna(row.get('total_wagons')) and str(row.get('total_wagons')).strip() else 20
                            )
                            db.add(rake)
                            seeded_count += 1

                            # Commit in batches of 50
                            if seeded_count % 50 == 0:
                                db.commit()
                                print(f"  → Committed batch of 50 rakes ({seeded_count}/{len(rakes_df)})")

                        except Exception as e:
                            print(f"  ⚠️  Error with rake row {idx}: {str(e)[:100]}...")
                            continue

                    db.commit()  # Final commit
                    print(f"✓ Seeded {seeded_count} rakes successfully")

                except Exception as e:
                    print(f"❌ Error seeding rakes: {e}")
                    db.rollback()
                    return False

            # Final verification
            final_inventory = db.query(InventoryItem).count()
            final_orders = db.query(Order).count()
            final_rakes = db.query(Rake).count()
            final_total = final_inventory + final_orders + final_rakes

            print(f"\n" + "=" * 60)
            print("SEEDING COMPLETE")
            print("=" * 60)
            print("Final database counts:")
            print(f"✓ Inventory items: {final_inventory} records")
            print(f"✓ Orders: {final_orders} records")
            print(f"✓ Rakes: {final_rakes} records")
            print(f"✓ Total: {final_total} records")
            print(f"✓ Records added: {final_total - total_before}")

            if final_total > 0:
                print("✅ Cloud database seeding successful!")
                print("🔄 Frontend will now display data from PostgreSQL")
            else:
                print("⚠️  No records were added - check CSV files")
                return False

        return True

    except Exception as e:
        print(f"❌ Critical error during seeding: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
