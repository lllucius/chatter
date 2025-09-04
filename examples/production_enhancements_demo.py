"""Example integration of production enhancements."""

import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.utils.performance_monitoring import (
    monitor_performance,
    monitor_database_query,
    performance_tracker
)
from chatter.utils.error_recovery import (
    with_retry,
    with_circuit_breaker, 
    RetryStrategy
)
from chatter.core.validation import validation_engine, DEFAULT_CONTEXT
from chatter.middleware.security import SecurityHeadersMiddleware


class EnhancedUserService:
    """Example service class with all production enhancements."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @with_circuit_breaker(failure_threshold=5, recovery_timeout=60)
    @with_retry(max_attempts=3, strategy=RetryStrategy.EXPONENTIAL_BACKOFF)
    @monitor_database_query("select", "users")
    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email with full production enhancements."""
        
        # Input validation and sanitization
        result = validation_engine.validate_input(email, "email", DEFAULT_CONTEXT)
        if not result.is_valid:
            raise ValueError(f"Invalid email: {result.errors[0].message}")
        
        safe_email = result.value
        
        # Simulate database query
        await asyncio.sleep(0.1)  # Simulate DB query time
        
        # Track custom metrics
        performance_tracker.track_database_query("user_lookup", 45.2, "users")
        
        return {
            "id": "user_123",
            "email": safe_email,
            "name": "John Doe",
            "active": True
        }
    
    @monitor_performance("user_creation")
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user with comprehensive validation."""
        
        # Comprehensive input validation using unified system
        # Validate required fields exist
        required_fields = ["email", "password", "username"]
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate and sanitize email
        result = validation_engine.validate_input(user_data["email"], "email", DEFAULT_CONTEXT)
        if not result.is_valid:
            raise ValueError(f"Email validation failed: {result.errors[0].message}")
        safe_email = result.value
        
        # Validate and sanitize username
        result = validation_engine.validate_input(user_data["username"], "username", DEFAULT_CONTEXT)
        if not result.is_valid:
            raise ValueError(f"Username validation failed: {result.errors[0].message}")
        safe_username = result.value
        
        # Validate password
        result = validation_engine.validate_input(user_data["password"], "password", DEFAULT_CONTEXT)
        if not result.is_valid:
            raise ValueError(f"Password validation failed: {result.errors[0].message}")
        safe_password = result.value
        
        safe_data = {
            "email": safe_email,
            "username": safe_username,
            "password": safe_password,
            **{k: v for k, v in user_data.items() if k not in required_fields}
        }
        
        # Simulate user creation
        await asyncio.sleep(0.2)
        
        return {
            "id": "user_456",
            "email": safe_data["email"],
            "username": safe_data["username"],
            "created": True
        }


def create_enhanced_app() -> FastAPI:
    """Create FastAPI app with all production enhancements."""
    
    app = FastAPI(
        title="Enhanced Chatter API",
        description="Production-ready API with comprehensive enhancements",
        version="1.0.0"
    )
    
    # Add security middleware
    app.add_middleware(SecurityHeadersMiddleware, strict_transport_security=True)
    
    # Example enhanced endpoint
    @app.get("/api/users/{email}")
    @monitor_performance("get_user_endpoint")
    async def get_user(email: str):
        """Get user by email with production enhancements."""
        try:
            # Create service instance (in real app, use dependency injection)
            user_service = EnhancedUserService(session=None)  # Mock session
            
            user = await user_service.get_user_by_email(email)
            return {"success": True, "user": user}
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.post("/api/users")
    @monitor_performance("create_user_endpoint")
    async def create_user(user_data: Dict[str, Any]):
        """Create user with comprehensive validation."""
        try:
            user_service = EnhancedUserService(session=None)  # Mock session
            
            user = await user_service.create_user(user_data)
            return {"success": True, "user": user}
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/admin/performance-metrics")
    async def get_performance_metrics():
        """Get comprehensive performance metrics."""
        return {
            "metrics": performance_tracker.get_performance_summary(),
            "status": "healthy"
        }
    
    return app


# Example usage and testing
async def example_usage():
    """Demonstrate enhanced functionality."""
    
    print("🚀 Production Enhancements Demo")
    print("=" * 50)
    
    # Create enhanced service
    service = EnhancedUserService(session=None)
    
    # Test 1: Valid user lookup
    print("\n📧 Testing valid email lookup...")
    try:
        user = await service.get_user_by_email("john.doe@example.com")
        print(f"✅ User found: {user['email']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Invalid email format
    print("\n📧 Testing invalid email format...")
    try:
        user = await service.get_user_by_email("invalid-email")
        print(f"✅ User found: {user['email']}")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid email: {e}")
    
    # Test 3: User creation with validation
    print("\n👤 Testing user creation...")
    valid_user_data = {
        "email": "newuser@example.com",
        "username": "newuser123",
        "password": "SecurePassword123!",
        "full_name": "New User"
    }
    
    try:
        user = await service.create_user(valid_user_data)
        print(f"✅ User created: {user['email']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: User creation with weak password
    print("\n🔒 Testing weak password rejection...")
    weak_password_data = {
        "email": "weakuser@example.com", 
        "username": "weakuser",
        "password": "weak",
        "full_name": "Weak User"
    }
    
    try:
        user = await service.create_user(weak_password_data)
        print(f"❌ Weak password accepted: {user['email']}")
    except ValueError as e:
        print(f"✅ Correctly rejected weak password: {e}")
    
    # Test 5: Performance metrics
    print("\n📊 Performance Metrics Summary:")
    metrics = performance_tracker.get_performance_summary()
    for metric_name, stats in metrics.items():
        print(f"  {metric_name}: avg={stats['avg']:.2f}ms, max={stats['max']:.2f}ms")
    
    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(example_usage())