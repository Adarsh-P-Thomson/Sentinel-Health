"""
Health check endpoints for monitoring database connectivity
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Dict, Any

from app.core.database import get_db, get_mongodb
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Basic health check")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    
    Returns application status and version
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/postgres", summary="PostgreSQL health check")
async def postgres_health_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check PostgreSQL database connectivity
    
    Tests:
    - Database connection
    - Query execution
    - Response time
    """
    try:
        start_time = datetime.utcnow()
        
        # Execute simple query
        result = await db.execute(text("SELECT 1 as health_check"))
        row = result.fetchone()
        
        end_time = datetime.utcnow()
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        if row and row[0] == 1:
            return {
                "status": "healthy",
                "database": "postgresql",
                "host": settings.postgres_host,
                "port": settings.postgres_port,
                "database_name": settings.postgres_db,
                "response_time_ms": round(response_time_ms, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PostgreSQL query returned unexpected result"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"PostgreSQL connection failed: {str(e)}"
        )


@router.get("/health/mongodb", summary="MongoDB health check")
async def mongodb_health_check(
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
) -> Dict[str, Any]:
    """
    Check MongoDB database connectivity
    
    Tests:
    - Database connection
    - Ping command
    - Response time
    """
    try:
        start_time = datetime.utcnow()
        
        # Execute ping command
        result = await db.command("ping")
        
        end_time = datetime.utcnow()
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        if result.get("ok") == 1:
            # Get collection count
            collections = await db.list_collection_names()
            
            return {
                "status": "healthy",
                "database": "mongodb",
                "host": settings.mongodb_host,
                "port": settings.mongodb_port,
                "database_name": settings.mongodb_db,
                "collections_count": len(collections),
                "response_time_ms": round(response_time_ms, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MongoDB ping command failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"MongoDB connection failed: {str(e)}"
        )


@router.get("/health/databases", summary="All databases health check")
async def all_databases_health_check(
    postgres_db: AsyncSession = Depends(get_db),
    mongodb: AsyncIOMotorDatabase = Depends(get_mongodb)
) -> Dict[str, Any]:
    """
    Check connectivity for all databases
    
    Returns status for:
    - PostgreSQL
    - MongoDB
    """
    results = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "databases": {}
    }
    
    # Check PostgreSQL
    try:
        start_time = datetime.utcnow()
        result = await postgres_db.execute(text("SELECT 1"))
        result.fetchone()
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        results["databases"]["postgresql"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2)
        }
    except Exception as e:
        results["status"] = "degraded"
        results["databases"]["postgresql"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check MongoDB
    try:
        start_time = datetime.utcnow()
        await mongodb.command("ping")
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        results["databases"]["mongodb"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2)
        }
    except Exception as e:
        results["status"] = "degraded"
        results["databases"]["mongodb"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Return appropriate status code
    if results["status"] == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=results
        )
    
    return results


@router.get("/health/detailed", summary="Detailed system health check")
async def detailed_health_check(
    postgres_db: AsyncSession = Depends(get_db),
    mongodb: AsyncIOMotorDatabase = Depends(get_mongodb)
) -> Dict[str, Any]:
    """
    Comprehensive health check with detailed system information
    
    Includes:
    - Application info
    - Database connectivity
    - Configuration status
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "application": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug_mode": settings.debug
        },
        "databases": {},
        "configuration": {
            "api_prefix": settings.api_prefix,
            "cors_enabled": len(settings.cors_origins) > 0,
            "swagger_ui_enabled": settings.enable_swagger_ui
        }
    }
    
    # PostgreSQL check
    try:
        start_time = datetime.utcnow()
        result = await postgres_db.execute(
            text("SELECT version(), current_database(), current_user")
        )
        row = result.fetchone()
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        health_data["databases"]["postgresql"] = {
            "status": "healthy",
            "host": settings.postgres_host,
            "port": settings.postgres_port,
            "database": settings.postgres_db,
            "user": settings.postgres_user,
            "response_time_ms": round(response_time, 2),
            "version": row[0].split()[1] if row else "unknown"
        }
    except Exception as e:
        health_data["status"] = "degraded"
        health_data["databases"]["postgresql"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # MongoDB check
    try:
        start_time = datetime.utcnow()
        server_info = await mongodb.client.server_info()
        collections = await mongodb.list_collection_names()
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        health_data["databases"]["mongodb"] = {
            "status": "healthy",
            "host": settings.mongodb_host,
            "port": settings.mongodb_port,
            "database": settings.mongodb_db,
            "collections_count": len(collections),
            "response_time_ms": round(response_time, 2),
            "version": server_info.get("version", "unknown")
        }
    except Exception as e:
        health_data["status"] = "degraded"
        health_data["databases"]["mongodb"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    if health_data["status"] == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_data
        )
    
    return health_data
