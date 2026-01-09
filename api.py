#!/usr/bin/env python3
"""
Habit Exposer API
Simple REST API to access stats

Run: uvicorn api:app --reload
Access: http://localhost:8000/stats
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from storage.database import DatabaseManager
from utils.config import Config

app = FastAPI(title="Habit Exposer API", version="1.0.0")

# Initialize database
config = Config.load()
db = DatabaseManager(config.storage.database_path)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Habit Exposer API",
        "endpoints": {
            "/stats": "Get summary statistics",
            "/stats/daily": "Get daily breakdown (last 7 days)",
            "/stats/hourly": "Get hourly breakdown (today)",
            "/events/recent": "Get recent events"
        }
    }


@app.get("/stats")
def get_stats():
    """Get summary statistics."""
    summary = db.get_statistics_summary()
    return JSONResponse(content=summary)


@app.get("/stats/daily")
def get_daily_stats(days: int = 7):
    """Get daily statistics."""
    daily = db.get_daily_statistics(days=days)
    return JSONResponse(content=daily)


@app.get("/stats/hourly")
def get_hourly_stats():
    """Get hourly statistics for today."""
    hourly = db.get_hourly_statistics()
    return JSONResponse(content=hourly)


@app.get("/events/recent")
def get_recent_events(limit: int = 10):
    """Get recent events."""
    events = db.get_recent_events(limit=limit)

    events_data = []
    for event in events:
        events_data.append({
            "event_id": event.event_uuid,
            "timestamp": event.timestamp.isoformat(),
            "frame_count": event.frame_count,
            "screenshot": event.screenshot_path
        })

    return JSONResponse(content=events_data)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Habit Exposer API...")
    print("📊 Access at: http://localhost:8000")
    print("📚 Docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
