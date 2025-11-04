import sys
import os
# Add the parent directory to sys.path to make 'app' package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.websockets import WebSocket
import asyncio
import json
import logging
from sqlalchemy.orm import Session

# Import database modules
from app.core.database import init_db, get_db
from app.core.config import settings

# Import routes
from app.routes import (
    dashboard,
    rake_allocation,
    order_management,
    inventory,
    ai_recommendations,
    live_simulation,
    reports,
    static_data
)

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="RakeVision AI API",
    description="Backend API for RakeVision AI - Rake Allocation and Quality Control System",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handler to initialize the database on startup
@app.on_event("startup")
async def startup_event():
    logging.info("Initializing database...")
    init_db()
    logging.info(f"Running in {settings.ENVIRONMENT} mode")
    logging.info(f"Database URI: {settings.SQLALCHEMY_DATABASE_URI}")

# Include all routers
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(rake_allocation.router, prefix="/api", tags=["Rake Allocation"])
app.include_router(order_management.router, prefix="/api", tags=["Orders"])
app.include_router(inventory.router, prefix="/api", tags=["Inventory"])
app.include_router(ai_recommendations.router, prefix="/api", tags=["AI Recommendations"])
app.include_router(live_simulation.router, prefix="/api", tags=["Live Simulation"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(static_data.router, prefix="/api", tags=["Static Data"])

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to RakeVision AI API"}

# WebSocket connection manager for simulation
class SimulationConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.simulation_running = False
        self.simulation_speed = 1
        self.rakes = []  # Will be loaded from database
        self.simulation_task = None
        self._db = None
        
    async def load_rakes_from_db(self):
        """Load active rakes from database"""
        try:
            # Get database session using next(get_db()) instead of using it as a dependency
            # This is needed because we're outside of a request context
            from app.services.simulation_service import get_active_rakes
            from app.models.rake import Rake
            from app.models.order import Order
            
            # Create a new session specifically for this method
            from app.core.database import SessionLocal
            db = SessionLocal()
            
            try:
                # Try to get real data from database
                active_rakes = []
                db_rakes = db.query(Rake).filter(Rake.status != "Idle").all()
                
                if db_rakes:
                    # Use real data
                    for rake in db_rakes:
                        # Get associated order for destination
                        order = db.query(Order).filter(Order.rake_id == rake.id).first()
                        destination = order.destination if order else "Unknown"
                        
                        active_rakes.append({
                            "id": rake.id,
                            "from": rake.origin_plant or "Bokaro",
                            "to": destination,
                            "progress": rake.transit_progress or 0,
                            "status": rake.status,
                            "departureTime": rake.departure_time.strftime("%H:%M %p") if rake.departure_time else "N/A",
                            "eta": rake.eta.strftime("%H:%M %p") if rake.eta else "N/A",
                            "freight": rake.freight_type or "N/A",
                            "weight": f"{rake.weight or 0} Tons"
                        })
                
                if active_rakes:
                    self.rakes = active_rakes
                else:
                    # Use fallback data if no rakes in database
                    self.rakes = [
                        {"id": "R1234", "from": "Bokaro", "to": "CMO Kolkata", "progress": 45, "status": "In Transit", "departureTime": "08:30 AM", "eta": "14:45 PM", "freight": "Steel Coils", "weight": "1250 Tons"},
                        {"id": "R5678", "from": "Bokaro", "to": "Customer A123", "progress": 78, "status": "In Transit", "departureTime": "07:15 AM", "eta": "12:30 PM", "freight": "Steel Plates", "weight": "980 Tons"},
                        {"id": "R9012", "from": "Bokaro", "to": "CMO Mumbai", "progress": 92, "status": "Arriving", "departureTime": "06:00 AM", "eta": "15:10 PM", "freight": "Steel Tubes", "weight": "1080 Tons"},
                        {"id": "R3456", "from": "Bokaro", "to": "Customer B456", "progress": 15, "status": "Departed", "departureTime": "09:45 AM", "eta": "18:20 PM", "freight": "Steel Beams", "weight": "1320 Tons"},
                    ]
            finally:
                # Always close the session
                db.close()
        except Exception as e:
            logging.error(f"Error loading rakes from database: {e}")
            # Use fallback data if error
            self.rakes = [
                {"id": "R1234", "from": "Bokaro", "to": "CMO Kolkata", "progress": 45, "status": "In Transit", "departureTime": "08:30 AM", "eta": "14:45 PM", "freight": "Steel Coils", "weight": "1250 Tons"},
                {"id": "R5678", "from": "Bokaro", "to": "Customer A123", "progress": 78, "status": "In Transit", "departureTime": "07:15 AM", "eta": "12:30 PM", "freight": "Steel Plates", "weight": "980 Tons"},
                {"id": "R9012", "from": "Bokaro", "to": "CMO Mumbai", "progress": 92, "status": "Arriving", "departureTime": "06:00 AM", "eta": "15:10 PM", "freight": "Steel Tubes", "weight": "1080 Tons"},
                {"id": "R3456", "from": "Bokaro", "to": "Customer B456", "progress": 15, "status": "Departed", "departureTime": "09:45 AM", "eta": "18:20 PM", "freight": "Steel Beams", "weight": "1320 Tons"},
            ]

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Load rakes from database
        await self.load_rakes_from_db()
        
        # Send initial status
        await websocket.send_json({
            "type": "simulation_status",
            "is_running": self.simulation_running,
            "speed": self.simulation_speed
        })
        
        # Send initial rake data
        await websocket.send_json({
            "type": "simulation_update",
            "rakes": self.rakes
        })

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_update_to_all(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Client might have disconnected
                pass

    async def start_simulation(self):
        self.simulation_running = True
        await self.send_update_to_all({
            "type": "simulation_status",
            "is_running": True,
            "speed": self.simulation_speed
        })
        
        # Cancel existing task if running
        if self.simulation_task:
            self.simulation_task.cancel()
        
        # Start new simulation task
        self.simulation_task = asyncio.create_task(self.simulation_loop())

    async def pause_simulation(self):
        self.simulation_running = False
        await self.send_update_to_all({
            "type": "simulation_status",
            "is_running": False,
            "speed": self.simulation_speed
        })
        
        # Cancel simulation task
        if self.simulation_task:
            self.simulation_task.cancel()
            self.simulation_task = None

    async def set_speed(self, speed: int):
        self.simulation_speed = max(1, min(3, speed))  # Clamp between 1-3
        await self.send_update_to_all({
            "type": "simulation_status",
            "is_running": self.simulation_running,
            "speed": self.simulation_speed
        })

    async def simulation_loop(self):
        """Main simulation loop that updates rake progress"""
        try:
            from app.models.rake import Rake
            
            while self.simulation_running:
                # Create a new session for database operations
                from app.core.database import SessionLocal
                db = SessionLocal()
                
                try:
                    # Update rake positions based on speed
                    for i, rake in enumerate(self.rakes):
                        if rake["progress"] < 100:
                            # Advance progress based on speed
                            rake["progress"] += 1 * self.simulation_speed
                            
                            # Cap at 100%
                            if rake["progress"] >= 100:
                                rake["progress"] = 100
                                rake["status"] = "Arrived"
                        
                        # Update status based on progress
                        if 90 <= rake["progress"] < 100:
                            rake["status"] = "Arriving"
                        elif 10 <= rake["progress"] < 90:
                            rake["status"] = "In Transit"
                        elif rake["progress"] < 10:
                            rake["status"] = "Departed"
                            
                        # Update database if we have real rakes
                        try:
                            # Find and update the rake in the database
                            db_rake = db.query(Rake).filter(Rake.id == rake["id"]).first()
                            if db_rake:
                                db_rake.transit_progress = rake["progress"]
                                db_rake.status = rake["status"]
                                # Update ETA based on progress
                                if rake["progress"] >= 100:
                                    from datetime import datetime
                                    db_rake.arrival_time = datetime.now()
                        except Exception as db_err:
                            logging.error(f"Error updating rake in database: {db_err}")
                    
                    # Commit changes to the database
                    db.commit()
                    
                    # Send updates to all clients
                    await self.send_update_to_all({
                        "type": "simulation_update",
                        "rakes": self.rakes
                    })
                    
                    # Wait before next update - time depends on speed
                    await asyncio.sleep(2 / self.simulation_speed)
                    
                    # Reset simulation if all rakes have arrived
                    if all(rake["progress"] >= 100 for rake in self.rakes):
                        # Reset all rakes
                        for rake in self.rakes:
                            rake["progress"] = 0
                            rake["status"] = "Departed"
                finally:
                    # Always close the session
                    db.close()
                
        except asyncio.CancelledError:
            # Simulation was paused
            pass
        except Exception as e:
            logging.error(f"Simulation error: {e}")
            await self.send_update_to_all({
                "type": "simulation_error",
                "message": f"Simulation error: {str(e)}"
            })
            self.simulation_running = False


# Create manager instance
simulation_manager = SimulationConnectionManager()

# WebSocket endpoint for live simulation
@app.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket):
    client = f"{websocket.client.host}:{websocket.client.port}" if hasattr(websocket, 'client') and websocket.client else "unknown"
    logging.info(f"WS connection attempt from {client}")
    try:
        await simulation_manager.connect(websocket)
        logging.info(f"WS connection accepted for {client}")
    except Exception as connection_err:
        logging.error(f"Error accepting WS connection: {connection_err}")
        raise
        
    try:
        while True:
            logging.debug(f"Waiting for message from {client}")
            data = await websocket.receive_text()
            logging.info(f"Received WS message from {client}: {data[:100]}...")
            try:
                # Parse client message
                message = json.loads(data)
                action = message.get("action")
                logging.debug(f"Parsed action: {action}")
                
                if action == "start_simulation":
                    await simulation_manager.start_simulation()
                elif action == "pause_simulation":
                    await simulation_manager.pause_simulation()
                elif action == "set_speed":
                    speed = message.get("speed", 1)
                    await simulation_manager.set_speed(speed)
            except json.JSONDecodeError as json_err:
                logging.error(f"JSON decode error from {client}: {json_err}")
                await websocket.send_json({
                    "type": "simulation_error",
                    "message": "Invalid JSON message"
                })
    except Exception as e:
        logging.exception(f"WebSocket error with {client}: {e}")
        print(f"WebSocket error: {e}")
    finally:
        logging.info(f"WS connection closed for {client}")
        simulation_manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
