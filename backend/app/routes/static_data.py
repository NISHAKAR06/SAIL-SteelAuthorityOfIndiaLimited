from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db
from app.models import rake, order, inventory
from app.models.cost_parameters import CostParameter
from app.models.route_transport import RouteTransport
import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)
router = APIRouter()

# Define the base path for static files
STATIC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "statics")

# Database seeding and management endpoints
@router.post("/database/seed")
async def seed_database(db: Session = Depends(get_db)):
    """
    Seed the database with sample data from CSV files
    """
    try:
        logger.info("Starting database seeding...")

        # Import CSV data and seed database tables
        from app.models.inventory import InventoryItem
        from app.models.order import Order
        from app.models.rake import Rake

        # Read CSV files and create database records
        inventory_df = pd.read_csv(os.path.join(STATIC_PATH, "production_inventory.csv"))
        orders_df = pd.read_csv(os.path.join(STATIC_PATH, "customer_orders.csv"))
        rakes_df = pd.read_csv(os.path.join(STATIC_PATH, "rake_wagon_details.csv"))

        seeded_counts = {
            "inventory_items": 0,
            "orders": 0,
            "rakes": 0
        }

        # Seed inventory items
        for _, row in inventory_df.iterrows():
            item = InventoryItem(
                plant_location=str(row.get('plant_location', 'Plant A')),
                product_name=str(row.get('product_name', 'Steel Product')),
                material_grade=str(row.get('material_grade', 'Grade A')),
                quantity=float(row.get('quantity', 1000)),
                unit=str(row.get('unit', 'tons')),
                storage_location=str(row.get('storage_location', 'Storage A')),
                next_production_date=None,
                production_rate=float(row.get('production_rate', 100)) if 'production_rate' in row and not pd.isna(row.get('production_rate')) else None
            )
            db.add(item)
            seeded_counts["inventory_items"] += 1

        # Seed orders
        for _, row in orders_df.iterrows():
            try:
                order = Order(
                    customer_name=str(row.get('customer_name', 'Customer A')).strip()[:100],
                    customer_id=int(float(row.get('customer_id', 1001))) if pd.notna(row.get('customer_id')) else None,
                    material=str(row.get('material', row.get('product_name', 'Steel'))).strip()[:100],
                    quantity=float(row.get('quantity', 500)),
                    unit=str(row.get('unit', 'tons')).strip()[:20],
                    status="pending",
                    priority="normal",
                    origin_plant=str(row.get('origin_plant', 'Plant A')).strip()[:100],
                    destination=str(row.get('destination', 'Location A')).strip()[:100],
                    rate_per_ton=float(row.get('rate_per_ton', 1000)) if pd.notna(row.get('rate_per_ton')) else None
                )
                db.add(order)
                seeded_counts["orders"] += 1
            except Exception as e:
                logger.warning(f"Failed to create order for row {_}: {e}")
                continue

        # Seed rakes
        for _, row in rakes_df.iterrows():
            rake = Rake(
                rake_number=str(row.get('rake_number', f'RK{1000 + _}')),
                origin_plant=str(row.get('origin_plant', 'Plant A')) if 'origin_plant' in row else 'Plant A',
                destination=str(row.get('destination', 'Location B')) if 'destination' in row else 'Location B',
                status=str(row.get('status', 'Available')),
                capacity_tons=float(row.get('capacity_tons', 2000)) if 'capacity_tons' in row and not pd.isna(row.get('capacity_tons')) else 2000,
                priority="normal",
                current_location=str(row.get('current_location', 'At Plant')) if 'current_location' in row else 'At Plant',
                total_wagons=int(row.get('total_wagons', 20)) if 'total_wagons' in row and not pd.isna(row.get('total_wagons')) else 20,
                last_maintenance_date=None
            )
            db.add(rake)
            seeded_counts["rakes"] += 1

        # Commit all changes
        db.commit()

        logger.info(f"Database seeded successfully: {seeded_counts}")

        return {
            "success": True,
            "message": "Database seeded successfully",
            "data": seeded_counts
        }

    except Exception as e:
        logger.error(f"Database seeding failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to seed database: {str(e)}")

@router.get("/database/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Get database statistics for all tables
    """
    try:
        from app.models.inventory import InventoryItem
        from app.models.order import Order
        from app.models.rake import Rake

        stats = {
            "inventory_items": db.query(InventoryItem).count(),
            "orders": db.query(Order).count(),
            "rakes": db.query(Rake).count()
        }

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"Failed to get database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")

def get_csv_file_path(filename: str) -> str:
    """Helper function to get full path to a CSV file in the statics folder"""
    return os.path.join(STATIC_PATH, filename)

@router.get("/static-data/files", response_model=List[str])
async def list_static_files():
    """
    Get a list of available static data files
    """
    try:
        files = [f for f in os.listdir(STATIC_PATH) if f.endswith('.csv')]
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list static files: {str(e)}")

@router.get("/static-data/{file_name}")
async def get_static_data(file_name: str, limit: Optional[int] = None):
    """
    Get data from a static CSV file with optional limit
    """
    file_path = get_csv_file_path(file_name)

    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {file_name} not found")

        df = pd.read_csv(file_path)

        # Process date fields for better frontend presentation
        for col in df.columns:
            if 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                except:
                    pass  # Ignore if column can't be converted

        # Apply limit if specified
        if limit:
            df = df.head(limit)

        # Convert to dict representation
        result = df.to_dict(orient='records')

        return {
            "file_name": file_name,
            "record_count": len(result),
            "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
            "columns": list(df.columns),
            "data": result
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to read {file_name}: {str(e)}")

@router.get("/static-data/summary/{file_name}")
async def get_static_data_summary(file_name: str):
    """
    Get a summary of data from a static CSV file
    """
    file_path = get_csv_file_path(file_name)

    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {file_name} not found")

        df = pd.read_csv(file_path)

        # Calculate basic statistics for numeric columns
        numeric_stats = {}
        for col in df.select_dtypes(include=['number']).columns:
            numeric_stats[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "avg": float(df[col].mean()),
                "sum": float(df[col].sum())
            }

        # Calculate counts for categorical columns
        categorical_counts = {}
        for col in df.select_dtypes(include=['object']).columns:
            counts = df[col].value_counts().to_dict()
            categorical_counts[col] = {str(k): int(v) for k, v in counts.items()}

        return {
            "file_name": file_name,
            "record_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "numeric_statistics": numeric_stats,
            "categorical_counts": categorical_counts
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to summarize {file_name}: {str(e)}")

@router.get("/static-data/production-inventory/current")
async def get_production_inventory(db: Session = Depends(get_db)):
    """
    Get the current production inventory with updated dates - SQL database integration
    """
    # Try SQL database first (for production)
    try:
        from app.models.inventory import InventoryItem

        # Get all inventory items from database
        inventory_items = db.query(InventoryItem).all()

        if inventory_items:
            logger.info(f"Retrieved {len(inventory_items)} inventory items from database")

            # Convert SQLAlchemy objects to dict and update dates
            result = []
            today = datetime.now()

            for i, item in enumerate(inventory_items):
                # Convert to dict and update production_schedule_date
                item_dict = {
                    "plant_location": item.plant_location,
                    "product_name": item.product_name,
                    "material_grade": item.material_grade,
                    "quantity": float(item.quantity),
                    "unit": item.unit,
                    "storage_location": item.storage_location,
                    "production_schedule_date": (today + timedelta(days=i % 5)).strftime('%Y-%m-%d'),
                    "next_production_date": item.next_production_date.isoformat() if item.next_production_date else None,
                    "production_rate": float(item.production_rate) if item.production_rate else 0,
                }
                result.append(item_dict)

            return {
                "last_updated": today.strftime('%Y-%m-%d %H:%M:%S'),
                "data": result,
                "source": "database"
            }

    except Exception as sql_error:
        logger.warning(f"Database query failed, falling back to CSV: {str(sql_error)}")

    # Fallback to CSV (for development)
    try:
        file_path = get_csv_file_path("production_inventory.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Production inventory file not found")

        df = pd.read_csv(file_path)

        # Update the dates to reflect current date
        today = datetime.now()
        df['production_schedule_date'] = [(today + timedelta(days=i % 5)).strftime('%Y-%m-%d') for i in range(len(df))]

        result = df.to_dict(orient='records')

        return {
            "last_updated": today.strftime('%Y-%m-%d %H:%M:%S'),
            "data": result,
            "source": "csv"
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get production inventory from database or CSV: {str(e)}")

@router.get("/static-data/customer-orders/current")
async def get_customer_orders(db: Session = Depends(get_db)):
    """
    Get customer orders with updated dates based on current date - SQL database integration
    """
    try:
        # Try SQL database first (for production)
        from app.models.order import Order

        # Get all orders from database
        orders = db.query(Order).all()

        if orders:
            logger.info(f"Retrieved {len(orders)} orders from database")

            # Convert SQLAlchemy objects to dict and update dates
            result = []
            today = datetime.now()

            for i, order in enumerate(orders):
                # Convert to dict and update dispatch/delivery dates
                order_dict = {
                    "order_id": order.id,
                    "customer_name": order.customer_name,
                    "customer_id": order.customer_id,
                    "material": order.material,
                    "quantity": float(order.quantity),
                    "unit": order.unit,
                    "preferred_dispatch_date": (today + timedelta(days=i % 30)).strftime('%Y-%m-%d'),
                    "latest_delivery_date": (today + timedelta(days=(i % 30) + 7 + (i % 7))).strftime('%Y-%m-%d'),
                    "order_status": order.status or "pending",
                    "priority": order.priority or "normal",
                    "origin_plant": order.origin_plant,
                    "destination": order.destination,
                    "rate_per_ton": float(order.rate_per_ton) if order.rate_per_ton else None,
                }
                result.append(order_dict)

            return {
                "last_updated": today.strftime('%Y-%m-%d %H:%M:%S'),
                "data": result,
                "source": "database"
            }

    except Exception as sql_error:
        logger.warning(f"Database query failed, falling back to CSV: {str(sql_error)}")

    # Fallback to CSV (for development)
    try:
        file_path = get_csv_file_path("customer_orders.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Customer orders file not found")

        df = pd.read_csv(file_path)

        # Update the dates to reflect current date
        today = datetime.now()

        # Set preferred dispatch dates to be within next 30 days
        df['preferred_dispatch_date'] = [(today + timedelta(days=i % 30)).strftime('%Y-%m-%d') for i in range(len(df))]

        # Set delivery dates to be 7-14 days after dispatch dates
        df['latest_delivery_date'] = [
            (datetime.strptime(dispatch_date, '%Y-%m-%d') + timedelta(days=7 + (i % 7))).strftime('%Y-%m-%d')
            for i, dispatch_date in enumerate(df['preferred_dispatch_date'])
        ]

        result = df.to_dict(orient='records')

        return {
            "last_updated": today.strftime('%Y-%m-%d %H:%M:%S'),
            "data": result,
            "source": "csv"
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get customer orders from database or CSV: {str(e)}")

@router.get("/static-data/rake-status/current")
async def get_rake_status(db: Session = Depends(get_db)):
    """
    Get current rake status with updated dates - SQL database integration
    """
    try:
        # Try SQL database first (for production)
        from app.models.rake import Rake

        # Get all rakes from database
        rakes = db.query(Rake).all()

        if rakes:
            logger.info(f"Retrieved {len(rakes)} rakes from database")

            # Convert SQLAlchemy objects to dict and update dates
            result = []
            today = datetime.now()

            for i, rake in enumerate(rakes):
                # Convert to dict and update operational dates
                rake_dict = {
                    "rake_id": rake.id,
                    "rake_number": rake.rake_number,
                    "origin_plant": rake.origin_plant,
                    "destination": rake.destination,
                    "status": rake.status or "Available",
                    "departure_date": (today + timedelta(days=i % 20 - 10)).strftime('%Y-%m-%d')
                                   if rake.status != 'Available' else None,
                    "expected_arrival_date": (today + timedelta(days=(i % 20 - 10) + 3 + (i % 7))).strftime('%Y-%m-%d')
                                           if rake.status != 'Available' else None,
                    "last_maintenance_date": (today - timedelta(days=i % 90)).strftime('%Y-%m-%d')
                                          if rake.last_maintenance_date else None,
                    "capacity_tons": float(rake.capacity_tons) if rake.capacity_tons else 0,
                    "priority": rake.priority or "normal",
                    "current_location": rake.current_location or "At Plant",
                    "total_wagons": rake.total_wagons or 0,
                }
                result.append(rake_dict)

            return {
                "last_updated": today.strftime('%Y-%m-%d %H:%M:%S'),
                "data": result,
                "source": "database"
            }

    except Exception as sql_error:
        logger.warning(f"Database query failed, falling back to CSV: {str(sql_error)}")

    # Fallback to CSV (for development)
    try:
        file_path = get_csv_file_path("rake_wagon_details.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Rake details file not found")

        df = pd.read_csv(file_path)

        # Update the dates to reflect current date
        today = datetime.now()

        # Set departure dates to be within past 10 days or future 10 days
        df['departure_date'] = [
            (today + timedelta(days=i % 20 - 10)).strftime('%Y-%m-%d')
            if df.iloc[i]['status'] != 'Available' and not pd.isna(df.iloc[i]['departure_date'])
            else None
            for i in range(len(df))
        ]

        # Set expected arrival dates to be 3-10 days after departure dates for in-transit rakes
        for i in range(len(df)):
            if df.iloc[i]['departure_date'] and df.iloc[i]['status'] == 'In-use':
                departure_date_val = df.iloc[i]['departure_date']
                if pd.notna(departure_date_val):
                    departure_date = datetime.strptime(str(departure_date_val), '%Y-%m-%d')
                    df.at[i, 'expected_arrival_date'] = (departure_date + timedelta(days=3 + (i % 7))).strftime('%Y-%m-%d')

        # Set last maintenance dates to be within past 90 days
        df['last_maintenance_date'] = [
            (today - timedelta(days=i % 90)).strftime('%Y-%m-%d')
            if not pd.isna(df.iloc[i]['last_maintenance_date'])
            else None
            for i in range(len(df))
        ]

        # Replace any NaN values with None for JSON serialization
        df = df.replace({np.nan: None})

        result = df.to_dict(orient='records')

        return {
            "last_updated": today.strftime('%Y-%m-%d %H:%M:%S'),
            "data": result,
            "source": "csv"
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get rake status from database or CSV: {str(e)}")

@router.get("/static-data/route_transport_info_updated.csv")
async def get_routes_csv():
    """
    Get the routes CSV file specifically
    """
    return await get_static_data("route_transport_info_updated.csv")


@router.get("/route-transport-info")
async def get_route_transport_info():
    """
    Get route transport info with proper JSON serialization
    """
    file_path = get_csv_file_path("route_transport_info_updated.csv")

    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Route transport info file not found")

        df = pd.read_csv(file_path)

        # Convert DataFrame to dictionary with proper NaN handling
        df = df.replace({np.nan: None})
        result = df.to_dict(orient='records')

        return {
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": result
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get route transport info: {str(e)}")
