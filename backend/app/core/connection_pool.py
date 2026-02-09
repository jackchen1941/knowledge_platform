"""
Advanced Database Connection Pool Management

This module provides sophisticated connection pool management,
monitoring, and optimization for different database types.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from sqlalchemy.pool import QueuePool, StaticPool, NullPool
from sqlalchemy.exc import DisconnectionError, TimeoutError as SQLTimeoutError
from sqlalchemy import event
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


@dataclass
class ConnectionStats:
    """Connection statistics tracking."""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_errors: List[str] = field(default_factory=list)
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    average_connection_time: float = 0.0
    peak_connections: int = 0
    total_requests: int = 0


@dataclass
class PoolMetrics:
    """Pool performance metrics."""
    pool_size: int
    max_overflow: int
    checked_out: int
    checked_in: int
    overflow: int
    invalid: int
    
    @property
    def utilization_percentage(self) -> float:
        """Calculate pool utilization percentage."""
        if self.pool_size == 0:
            return 0.0
        return (self.checked_out / (self.pool_size + self.overflow)) * 100


class ConnectionPoolManager:
    """Advanced connection pool management and monitoring."""
    
    def __init__(self):
        self.stats = ConnectionStats()
        self.connection_times: List[float] = []
        self.max_connection_time_samples = 100
        self._monitoring_task: Optional[asyncio.Task] = None
        self._pool_events_registered = False
    
    def register_pool_events(self, engine) -> None:
        """Register pool event listeners for monitoring."""
        if self._pool_events_registered:
            return
        
        @event.listens_for(engine.pool, "connect")
        def on_connect(dbapi_conn, connection_record):
            """Handle new connection creation."""
            self.stats.total_connections += 1
            self.stats.active_connections += 1
            self.stats.peak_connections = max(
                self.stats.peak_connections, 
                self.stats.active_connections
            )
            logger.debug(f"New database connection created. Total: {self.stats.total_connections}")
        
        @event.listens_for(engine.pool, "checkout")
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            """Handle connection checkout."""
            start_time = time.time()
            connection_record.info['checkout_time'] = start_time
            self.stats.total_requests += 1
            logger.debug("Database connection checked out")
        
        @event.listens_for(engine.pool, "checkin")
        def on_checkin(dbapi_conn, connection_record):
            """Handle connection checkin."""
            if 'checkout_time' in connection_record.info:
                connection_time = time.time() - connection_record.info['checkout_time']
                self._record_connection_time(connection_time)
                del connection_record.info['checkout_time']
            logger.debug("Database connection checked in")
        
        @event.listens_for(engine.pool, "close")
        def on_close(dbapi_conn, connection_record):
            """Handle connection close."""
            self.stats.active_connections = max(0, self.stats.active_connections - 1)
            logger.debug("Database connection closed")
        
        @event.listens_for(engine.pool, "close_detached")
        def on_close_detached(dbapi_conn):
            """Handle detached connection close."""
            logger.debug("Detached database connection closed")
        
        @event.listens_for(engine.pool, "invalidate")
        def on_invalidate(dbapi_conn, connection_record, exception):
            """Handle connection invalidation."""
            self.stats.failed_connections += 1
            error_msg = f"Connection invalidated: {exception}"
            self.stats.connection_errors.append(error_msg)
            self.stats.last_error = error_msg
            self.stats.last_error_time = datetime.utcnow()
            
            # Keep only last 10 errors
            if len(self.stats.connection_errors) > 10:
                self.stats.connection_errors = self.stats.connection_errors[-10:]
            
            logger.warning(f"Database connection invalidated: {exception}")
        
        self._pool_events_registered = True
        logger.info("Pool event listeners registered")
    
    def _record_connection_time(self, connection_time: float) -> None:
        """Record connection time for statistics."""
        self.connection_times.append(connection_time)
        
        # Keep only recent samples
        if len(self.connection_times) > self.max_connection_time_samples:
            self.connection_times = self.connection_times[-self.max_connection_time_samples:]
        
        # Update average
        self.stats.average_connection_time = sum(self.connection_times) / len(self.connection_times)
    
    def get_pool_metrics(self, engine) -> PoolMetrics:
        """Get current pool metrics."""
        pool = engine.pool
        
        # 检查是否为SQLite的StaticPool
        if isinstance(pool, StaticPool):
            # SQLite使用StaticPool，返回模拟的指标
            return PoolMetrics(
                pool_size=1,  # SQLite通常只有一个连接
                max_overflow=0,
                checked_out=0,
                checked_in=1,
                overflow=0,
                invalid=0,
            )
        
        # 对于其他类型的连接池
        return PoolMetrics(
            pool_size=pool.size(),
            max_overflow=pool._max_overflow,
            checked_out=pool.checkedout(),
            checked_in=pool.checkedin(),
            overflow=pool.overflow(),
            invalid=pool.invalid(),
        )
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics."""
        return {
            "total_connections": self.stats.total_connections,
            "active_connections": self.stats.active_connections,
            "failed_connections": self.stats.failed_connections,
            "peak_connections": self.stats.peak_connections,
            "total_requests": self.stats.total_requests,
            "average_connection_time_ms": round(self.stats.average_connection_time * 1000, 2),
            "recent_errors": self.stats.connection_errors[-5:],  # Last 5 errors
            "last_error": self.stats.last_error,
            "last_error_time": self.stats.last_error_time.isoformat() if self.stats.last_error_time else None,
        }
    
    def get_pool_health_status(self, engine) -> Dict[str, Any]:
        """Get pool health status and recommendations."""
        metrics = self.get_pool_metrics(engine)
        stats = self.get_connection_stats()
        
        # Calculate health indicators
        utilization = metrics.utilization_percentage
        error_rate = (stats["failed_connections"] / max(stats["total_requests"], 1)) * 100
        
        # Determine health status
        if error_rate > 10:
            health_status = "critical"
        elif error_rate > 5 or utilization > 90:
            health_status = "warning"
        elif utilization > 70:
            health_status = "moderate"
        else:
            health_status = "healthy"
        
        # Generate recommendations
        recommendations = []
        if utilization > 90:
            recommendations.append("Consider increasing pool size")
        if error_rate > 5:
            recommendations.append("High error rate detected, check database connectivity")
        if stats["average_connection_time_ms"] > 1000:
            recommendations.append("High connection time, consider connection pooling optimization")
        if metrics.overflow > metrics.pool_size * 0.5:
            recommendations.append("High overflow usage, consider increasing max_overflow")
        
        return {
            "health_status": health_status,
            "utilization_percentage": round(utilization, 2),
            "error_rate_percentage": round(error_rate, 2),
            "recommendations": recommendations,
            "metrics": {
                "pool_size": metrics.pool_size,
                "max_overflow": metrics.max_overflow,
                "checked_out": metrics.checked_out,
                "checked_in": metrics.checked_in,
                "overflow": metrics.overflow,
                "invalid": metrics.invalid,
            },
            "statistics": stats,
        }
    
    async def start_monitoring(self, engine, interval: int = 60) -> None:
        """Start background pool monitoring."""
        if self._monitoring_task and not self._monitoring_task.done():
            return
        
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(engine, interval)
        )
        logger.info(f"Started pool monitoring with {interval}s interval")
    
    async def stop_monitoring(self) -> None:
        """Stop background pool monitoring."""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped pool monitoring")
    
    async def _monitoring_loop(self, engine, interval: int) -> None:
        """Background monitoring loop."""
        while True:
            try:
                await asyncio.sleep(interval)
                
                # 检查是否为SQLite，如果是则跳过详细监控
                if isinstance(engine.pool, StaticPool):
                    logger.debug("SQLite使用StaticPool，跳过详细连接池监控")
                    continue
                
                health_status = self.get_pool_health_status(engine)
                
                # Log warnings for unhealthy pools
                if health_status["health_status"] in ["warning", "critical"]:
                    logger.warning(
                        f"Pool health: {health_status['health_status']} - "
                        f"Utilization: {health_status['utilization_percentage']}% - "
                        f"Error rate: {health_status['error_rate_percentage']}%"
                    )
                    
                    for recommendation in health_status["recommendations"]:
                        logger.warning(f"Recommendation: {recommendation}")
                
                # Log periodic health summary
                if health_status["health_status"] == "healthy":
                    logger.debug(
                        f"Pool healthy - Utilization: {health_status['utilization_percentage']}% - "
                        f"Active connections: {health_status['metrics']['checked_out']}"
                    )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in pool monitoring: {e}")
    
    async def optimize_pool_settings(self, engine) -> Dict[str, Any]:
        """Analyze usage patterns and suggest pool optimizations."""
        health_status = self.get_pool_health_status(engine)
        metrics = health_status["metrics"]
        stats = health_status["statistics"]
        
        suggestions = {
            "current_settings": {
                "pool_size": metrics["pool_size"],
                "max_overflow": metrics["max_overflow"],
            },
            "suggested_settings": {},
            "reasoning": [],
        }
        
        # Analyze utilization patterns
        utilization = health_status["utilization_percentage"]
        
        if utilization > 90:
            # High utilization - suggest increasing pool size
            new_pool_size = min(metrics["pool_size"] * 2, 50)  # Cap at 50
            suggestions["suggested_settings"]["pool_size"] = new_pool_size
            suggestions["reasoning"].append(
                f"High utilization ({utilization}%) suggests increasing pool size to {new_pool_size}"
            )
        elif utilization < 30 and metrics["pool_size"] > 5:
            # Low utilization - suggest decreasing pool size
            new_pool_size = max(metrics["pool_size"] // 2, 5)  # Minimum of 5
            suggestions["suggested_settings"]["pool_size"] = new_pool_size
            suggestions["reasoning"].append(
                f"Low utilization ({utilization}%) suggests decreasing pool size to {new_pool_size}"
            )
        
        # Analyze overflow usage
        if metrics["overflow"] > metrics["pool_size"] * 0.5:
            new_max_overflow = metrics["max_overflow"] * 2
            suggestions["suggested_settings"]["max_overflow"] = new_max_overflow
            suggestions["reasoning"].append(
                f"High overflow usage suggests increasing max_overflow to {new_max_overflow}"
            )
        
        # Analyze error patterns
        if health_status["error_rate_percentage"] > 5:
            suggestions["reasoning"].append(
                "High error rate detected - consider checking database connectivity and timeout settings"
            )
        
        return suggestions


# Global pool manager instance
pool_manager = ConnectionPoolManager()


@asynccontextmanager
async def managed_connection(engine):
    """Context manager for managed database connections with monitoring."""
    start_time = time.time()
    connection = None
    
    try:
        async with engine.begin() as conn:
            connection = conn
            yield conn
    except DisconnectionError as e:
        pool_manager.stats.failed_connections += 1
        logger.error(f"Database disconnection error: {e}")
        raise
    except SQLTimeoutError as e:
        pool_manager.stats.failed_connections += 1
        logger.error(f"Database timeout error: {e}")
        raise
    except Exception as e:
        pool_manager.stats.failed_connections += 1
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        connection_time = time.time() - start_time
        pool_manager._record_connection_time(connection_time)


def get_pool_manager() -> ConnectionPoolManager:
    """Get the global pool manager instance."""
    return pool_manager