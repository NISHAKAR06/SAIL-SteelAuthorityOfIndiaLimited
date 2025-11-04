#!/usr/bin/env python3

import sys
import os
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Define all models to match existing ones
class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_location = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    material_grade = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, default='tons')
    storage_location = Column(String, nullable=False)
    production_schedule_date = Column(String)
    available_for_dispatch = Column(Float)
    reorder_level = Column(Float)
    allocated_for_orders = Column(Float)

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
    preferred_dispatch_date = Column(String)
    latest_delivery_date = Column(String)
    rake_id = Column(Integer, nullable=True)

class Rake(Base):
    __tablename__ = 'rakes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rake_number = Column(String(50), nullable=False, unique=True)
    rake_type = Column(String, nullable=True)
    origin_plant = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    status = Column(String(50), default='Available')
    capacity_tons = Column(Float, nullable=False, default=0.0)
    priority = Column(String(20), default='normal')
    current_location = Column(String(100), nullable=True)
    total_wagons = Column(Integer, nullable=False, default=0)
    available_wagons = Column(Integer, nullable=True)
    commodity_compatibility = Column(String, nullable=True)
    assigned_orders = Column(String, nullable=True)
    departure_date = Column(String, nullable=True)
    expected_arrival_date = Column(String, nullable=True)
    last_maintenance_date = Column(String, nullable=True)

class CostParameter(Base):
    __tablename__ = "cost_parameters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    cost_per_tonne_km = Column(Float, nullable=False)
    loading_cost_per_wagon = Column(Float, nullable=False)
    unloading_cost_per_wagon = Column(Float, nullable=False)
    penalty_per_day_delay = Column(Float, nullable=False)
    priority_multiplier = Column(Float, nullable=False)
    fuel_surcharge_per_wagon = Column(Float, nullable=False)

class RouteTransport(Base):
    __tablename__ = "route_transport_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    transit_time_days = Column(Integer, nullable=False)
    preferred_route = Column(String, nullable=False)
    alternate_route = Column(String, nullable=True)
    track_capacity_wagons_per_day = Column(Integer, nullable=False)
    route_constraints = Column(String, nullable=True)
    expected_delays_days = Column(Integer, nullable=True)
    railway_zone = Column(String, nullable=False)

def seed_all_csv_data():
    """Seed all CSV data to cloud database"""

    print("=" * 60)
    print("SAIL DSS Cloud Database Complete Seeding")
    print("=" * 60)

    try:
        print("\nConnecting to cloud database...")
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created")

        statics_path = 'statics'
        seeded_totals = {}

        with SessionLocal() as db:

            # 1. Seed cost parameters
            print("\n🌱 Seeding cost parameters...")
            cost_df = pd.read_csv(os.path.join(statics_path, 'cost_parameters.csv'))
            cost_count = 0
            for _, row in cost_df.iterrows():
                cost_param = CostParameter(
                    commodity=str(row['commodity']),
                    priority=str(row['priority']),
                    cost_per_tonne_km=float(row['cost_per_tonne_km']),
                    loading_cost_per_wagon=float(row['loading_cost_per_wagon']),
                    unloading_cost_per_wagon=float(row['unloading_cost_per_wagon']),
                    penalty_per_day_delay=float(row['penalty_per_day_delay']),
                    priority_multiplier=float(row['priority_multiplier']),
                    fuel_surcharge_per_wagon=float(row['fuel_surcharge_per_wagon'])
                )
                db.add(cost_param)
                cost_count += 1
            db.commit()
            seeded_totals['cost_parameters'] = cost_count

            # 2. Seed route transport info
            print("🌱 Seeding route transport information...")
            route_df = pd.read_csv(os.path.join(statics_path, 'route_transport_info_updated.csv'))
            route_count = 0
            for _, row in route_df.iterrows():
                route = RouteTransport(
                    origin=str(row['origin']),
                    destination=str(row['destination']),
                    distance_km=float(row['distance_km']),
                    transit_time_days=int(row['transit_time_days']),
                    preferred_route=str(row['preferred_route']),
                    alternate_route=str(row['alternate_route']) if pd.notna(row.get('alternate_route')) else None,
                    track_capacity_wagons_per_day=int(row['track_capacity_wagons_per_day']),
                    route_constraints=str(row['route_constraints']) if pd.notna(row.get('route_constraints')) else None,
                    expected_delays_days=int(row['expected_delays_days']) if pd.notna(row.get('expected_delays_days')) else None,
                    railway_zone=str(row['railway_zone'])
                )
                db.add(route)
                route_count += 1
            db.commit()
            seeded_totals['route_transport'] = route_count

            # 3. Seed customer orders
            print("🌱 Seeding customer orders...")
            orders_df = pd.read_csv(os.path.join(statics_path, 'customer_orders.csv'))
            orders_count = 0
            for _, row in orders_df.iterrows():
                order = Order(
                    customer_name=str(row['customer_name']),
                    material=str(row['commodity']),
                    quantity=float(row['order_quantity_tonnes']),
                    unit='tons',
                    status=str(row['order_status']),
                    priority=str(row['priority']),
                    origin_plant=str(row.get('origin_plant', 'Bokaro')),
                    destination=str(row['destination']),
                    preferred_dispatch_date=str(row['preferred_dispatch_date']),
                    latest_delivery_date=str(row['latest_delivery_date'])
                )
                db.add(order)
                orders_count += 1
            db.commit()
            seeded_totals['orders'] = orders_count

            # 4. Seed rake details
            print("🌱 Seeding rake details...")
            rakes_df = pd.read_csv(os.path.join(statics_path, 'rake_wagon_details.csv'))
            rakes_count = 0
            for _, row in rakes_df.iterrows():
                rake = Rake(
                    rake_number=str(row['rake_number']),
                    rake_type=str(row['rake_type']),
                    origin_plant='Bokaro',  # Default to main plant
                    destination=str(row.get('destination', 'Various')),
                    status=str(row['status']),
                    capacity_tons=float(row.get('total_wagons', 20) * 100),  # Assume 100 tons per wagon
                    current_location=str(row['current_location']),
                    total_wagons=int(row['total_wagons']),
                    available_wagons=int(row['available_wagons']),
                    commodity_compatibility=str(row['commodity_compatibility']),
                    assigned_orders=str(row['assigned_orders']) if pd.notna(row.get('assigned_orders')) else None,
                    departure_date=str(row['departure_date']) if pd.notna(row.get('departure_date')) else None,
                    expected_arrival_date=str(row['expected_arrival_date']) if pd.notna(row.get('expected_arrival_date')) else None,
                    last_maintenance_date=str(row['last_maintenance_date']) if pd.notna(row.get('last_maintenance_date')) else None
                )
                db.add(rake)
                rakes_count += 1
            db.commit()
            seeded_totals['rakes'] = rakes_count

            # 5. Seed production inventory
            print("🌱 Seeding production inventory...")
            inventory_df = pd.read_csv(os.path.join(statics_path, 'production_inventory.csv'))
            inventory_count = 0
            for _, row in inventory_df.iterrows():
                item = InventoryItem(
                    plant_location='Bokaro',  # Default plant
                    product_name=str(row['product']),
                    material_grade='Grade A',
                    quantity=float(row['inventory_tonnes']),
                    unit='tons',
                    storage_location=f'Storage Area {inventory_count + 1}',
                    production_schedule_date=str(row['production_schedule_date']),
                    available_for_dispatch=float(row['available_for_dispatch']),
                    reorder_level=float(row.get('reorder_level_tonnes', 1000)),
                    allocated_for_orders=float(row['allocated_for_orders'])
                )
                db.add(item)
                inventory_count += 1
            db.commit()
            seeded_totals['inventory'] = inventory_count

            # Final verification
            grand_total = sum(seeded_totals.values())

            print("\n" + "=" * 60)
            print("COMPLETE DATABASE SEEDING SUCCESS!")
            print("=" * 60)
            print("All CSV data successfully stored in cloud database:")
            print(f"✓ Cost Parameters: {seeded_totals['cost_parameters']} records")
            print(f"✓ Route Transport: {seeded_totals['route_transport']} records")
            print(f"✓ Customer Orders: {seeded_totals['orders']} records")
            print(f"✓ Rake Details: {seeded_totals['rakes']} records")
            print(f"✓ Production Inventory: {seeded_totals['inventory']} records")
            print(f"✓ TOTAL RECORDS: {grand_total}")

            print(f"\n✅ All {len(seeded_totals)} CSV files converted to database tables")
            print("🔄 Frontend will now fetch all data from PostgreSQL database")
            print("🚀 System is ready for production use with cloud storage!")

        return True

    except Exception as e:
        print(f"❌ Critical error during seeding: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_all_csv_data()
    print(f"\nSeeding {'successful' if success else 'failed'}!")
    sys.exit(0 if success else 1)
