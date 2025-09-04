"""Security monitoring and alerting system for authentication events."""

import asyncio
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional
from enum import Enum

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SecurityEventType(Enum):
    """Types of security events to monitor."""
    
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGIN_BLOCKED = "login_blocked"
    
    # Account events
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_DEACTIVATED = "account_deactivated"
    
    # Password events
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"
    
    # Token events
    TOKEN_CREATED = "token_created"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"
    TOKEN_BLACKLISTED = "token_blacklisted"
    
    # API key events
    API_KEY_CREATED = "api_key_created"
    API_KEY_USED = "api_key_used"
    API_KEY_REVOKED = "api_key_revoked"
    
    # Suspicious activity
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    ANOMALOUS_LOGIN = "anomalous_login"
    MULTIPLE_FAILURES = "multiple_failures"
    SUSPICIOUS_IP = "suspicious_ip"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Security violations
    DISPOSABLE_EMAIL_BLOCKED = "disposable_email_blocked"
    WEAK_PASSWORD_REJECTED = "weak_password_rejected"
    PERSONAL_INFO_PASSWORD = "personal_info_password"


class SecurityEventSeverity(Enum):
    """Security event severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent:
    """Represents a security event."""
    
    def __init__(
        self,
        event_type: SecurityEventType,
        severity: SecurityEventSeverity,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.event_type = event_type
        self.severity = severity
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.details = details or {}
        self.timestamp = timestamp or datetime.now(UTC)
        self.event_id = self._generate_event_id()
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class SecurityMonitor:
    """Security monitoring and alerting system."""
    
    def __init__(self, cache_service=None):
        """Initialize security monitor.
        
        Args:
            cache_service: Cache service for storing security data
        """
        self.cache = cache_service
        self._alert_handlers: List[callable] = []
        
        # Thresholds for alerting
        self.thresholds = {
            "failed_logins_per_ip": 10,
            "failed_logins_per_user": 5,
            "password_resets_per_hour": 5,
            "registrations_per_ip_per_hour": 3,
            "api_key_usage_anomaly": 100
        }
        
        # Time windows for analysis
        self.time_windows = {
            "short": timedelta(minutes=15),
            "medium": timedelta(hours=1),
            "long": timedelta(hours=24)
        }
    
    def add_alert_handler(self, handler: callable):
        """Add alert handler function.
        
        Args:
            handler: Function to call when alert is triggered
        """
        self._alert_handlers.append(handler)
    
    async def log_security_event(self, event: SecurityEvent):
        """Log a security event and check for alerts.
        
        Args:
            event: Security event to log
        """
        try:
            # Log the event
            logger.info(
                f"Security event: {event.event_type.value}",
                event_id=event.event_id,
                severity=event.severity.value,
                user_id=event.user_id,
                ip_address=event.ip_address,
                **event.details
            )
            
            # Store in cache for analysis
            if self.cache:
                await self._store_security_event(event)
            
            # Check for patterns and alerts
            await self._analyze_security_patterns(event)
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def _store_security_event(self, event: SecurityEvent):
        """Store security event in cache for analysis.
        
        Args:
            event: Security event to store
        """
        try:
            # Store individual event
            event_key = f"security_event:{event.event_id}"
            await self.cache.set(event_key, event.to_dict(), timedelta(days=7))
            
            # Add to daily events list
            date_key = f"security_events:{event.timestamp.date()}"
            daily_events = await self.cache.get(date_key) or []
            daily_events.append(event.event_id)
            
            # Keep only last 1000 events per day
            if len(daily_events) > 1000:
                daily_events = daily_events[-1000:]
            
            await self.cache.set(date_key, daily_events, timedelta(days=7))
            
            # Update event type counters
            await self._update_event_counters(event)
            
        except Exception as e:
            logger.error(f"Failed to store security event: {e}")
    
    async def _update_event_counters(self, event: SecurityEvent):
        """Update event counters for analysis.
        
        Args:
            event: Security event
        """
        try:
            # Counter keys
            keys = [
                f"event_count:{event.event_type.value}:hour",
                f"event_count:{event.event_type.value}:day",
            ]
            
            if event.ip_address:
                keys.extend([
                    f"event_count_ip:{event.ip_address}:{event.event_type.value}:hour",
                    f"event_count_ip:{event.ip_address}:{event.event_type.value}:day",
                ])
            
            if event.user_id:
                keys.extend([
                    f"event_count_user:{event.user_id}:{event.event_type.value}:hour",
                    f"event_count_user:{event.user_id}:{event.event_type.value}:day",
                ])
            
            # Increment counters
            for key in keys:
                expire_time = timedelta(hours=25) if "hour" in key else timedelta(days=8)
                current_count = await self.cache.get(key) or 0
                await self.cache.set(key, current_count + 1, expire_time)
                
        except Exception as e:
            logger.debug(f"Failed to update event counters: {e}")
    
    async def _analyze_security_patterns(self, event: SecurityEvent):
        """Analyze security patterns and trigger alerts.
        
        Args:
            event: Security event to analyze
        """
        try:
            # Check for specific patterns based on event type
            if event.event_type == SecurityEventType.LOGIN_FAILURE:
                await self._check_brute_force_patterns(event)
                
            elif event.event_type == SecurityEventType.PASSWORD_RESET_REQUESTED:
                await self._check_password_reset_abuse(event)
                
            elif event.event_type == SecurityEventType.ACCOUNT_CREATED:
                await self._check_registration_patterns(event)
                
            elif event.event_type == SecurityEventType.API_KEY_USED:
                await self._check_api_key_anomalies(event)
                
            # Check for general anomalies
            await self._check_general_anomalies(event)
            
        except Exception as e:
            logger.error(f"Security pattern analysis failed: {e}")
    
    async def _check_brute_force_patterns(self, event: SecurityEvent):
        """Check for brute force attack patterns.
        
        Args:
            event: Login failure event
        """
        if not self.cache or not event.ip_address:
            return
        
        # Check failed login count for IP
        ip_failures_key = f"event_count_ip:{event.ip_address}:login_failure:hour"
        ip_failures = await self.cache.get(ip_failures_key) or 0
        
        if ip_failures >= self.thresholds["failed_logins_per_ip"]:
            await self._trigger_alert(
                SecurityEventType.BRUTE_FORCE_ATTEMPT,
                SecurityEventSeverity.HIGH,
                f"Brute force attack detected from IP {event.ip_address}",
                {
                    "ip_address": event.ip_address,
                    "failure_count": ip_failures,
                    "time_window": "1 hour"
                }
            )
        
        # Check failed login count for user
        if event.user_id:
            user_failures_key = f"event_count_user:{event.user_id}:login_failure:hour"
            user_failures = await self.cache.get(user_failures_key) or 0
            
            if user_failures >= self.thresholds["failed_logins_per_user"]:
                await self._trigger_alert(
                    SecurityEventType.MULTIPLE_FAILURES,
                    SecurityEventSeverity.MEDIUM,
                    f"Multiple login failures for user {event.user_id}",
                    {
                        "user_id": event.user_id,
                        "failure_count": user_failures,
                        "time_window": "1 hour"
                    }
                )
    
    async def _check_password_reset_abuse(self, event: SecurityEvent):
        """Check for password reset abuse patterns.
        
        Args:
            event: Password reset event
        """
        if not self.cache or not event.ip_address:
            return
        
        # Check password reset count for IP
        reset_key = f"event_count_ip:{event.ip_address}:password_reset_requested:hour"
        reset_count = await self.cache.get(reset_key) or 0
        
        if reset_count >= self.thresholds["password_resets_per_hour"]:
            await self._trigger_alert(
                SecurityEventType.SUSPICIOUS_IP,
                SecurityEventSeverity.MEDIUM,
                f"Excessive password reset requests from IP {event.ip_address}",
                {
                    "ip_address": event.ip_address,
                    "reset_count": reset_count,
                    "time_window": "1 hour"
                }
            )
    
    async def _check_registration_patterns(self, event: SecurityEvent):
        """Check for suspicious registration patterns.
        
        Args:
            event: Account creation event
        """
        if not self.cache or not event.ip_address:
            return
        
        # Check registration count for IP
        reg_key = f"event_count_ip:{event.ip_address}:account_created:hour"
        reg_count = await self.cache.get(reg_key) or 0
        
        if reg_count >= self.thresholds["registrations_per_ip_per_hour"]:
            await self._trigger_alert(
                SecurityEventType.SUSPICIOUS_IP,
                SecurityEventSeverity.MEDIUM,
                f"Multiple registrations from IP {event.ip_address}",
                {
                    "ip_address": event.ip_address,
                    "registration_count": reg_count,
                    "time_window": "1 hour"
                }
            )
    
    async def _check_api_key_anomalies(self, event: SecurityEvent):
        """Check for API key usage anomalies.
        
        Args:
            event: API key usage event
        """
        if not self.cache or not event.user_id:
            return
        
        # Check API key usage count
        usage_key = f"event_count_user:{event.user_id}:api_key_used:hour"
        usage_count = await self.cache.get(usage_key) or 0
        
        if usage_count >= self.thresholds["api_key_usage_anomaly"]:
            await self._trigger_alert(
                SecurityEventType.ANOMALOUS_LOGIN,
                SecurityEventSeverity.MEDIUM,
                f"Unusual API key usage pattern for user {event.user_id}",
                {
                    "user_id": event.user_id,
                    "usage_count": usage_count,
                    "time_window": "1 hour"
                }
            )
    
    async def _check_general_anomalies(self, event: SecurityEvent):
        """Check for general security anomalies.
        
        Args:
            event: Security event
        """
        # Check for events from unusual locations
        if event.ip_address and event.user_id:
            await self._check_location_anomalies(event)
        
        # Check for events at unusual times
        await self._check_time_anomalies(event)
    
    async def _check_location_anomalies(self, event: SecurityEvent):
        """Check for location-based anomalies.
        
        Args:
            event: Security event with IP and user
        """
        try:
            # Get recent IPs for user
            user_ips_key = f"user_ips:{event.user_id}"
            recent_ips = await self.cache.get(user_ips_key) or []
            
            # If this is a new IP for the user, flag as potential anomaly
            if event.ip_address not in recent_ips:
                # Add to recent IPs
                recent_ips.append(event.ip_address)
                recent_ips = recent_ips[-10:]  # Keep last 10 IPs
                await self.cache.set(user_ips_key, recent_ips, timedelta(days=30))
                
                # If user has other IPs, this might be anomalous
                if len(recent_ips) > 1:
                    await self._trigger_alert(
                        SecurityEventType.ANOMALOUS_LOGIN,
                        SecurityEventSeverity.LOW,
                        f"Login from new IP address for user {event.user_id}",
                        {
                            "user_id": event.user_id,
                            "new_ip": event.ip_address,
                            "known_ips": len(recent_ips) - 1
                        }
                    )
                    
        except Exception as e:
            logger.debug(f"Location anomaly check failed: {e}")
    
    async def _check_time_anomalies(self, event: SecurityEvent):
        """Check for time-based anomalies.
        
        Args:
            event: Security event
        """
        try:
            # Check if login is at unusual hour (e.g., 2-6 AM)
            if event.event_type in [SecurityEventType.LOGIN_SUCCESS, SecurityEventType.API_KEY_USED]:
                hour = event.timestamp.hour
                
                # Flag logins between 2 AM and 6 AM as potentially unusual
                if 2 <= hour <= 6:
                    await self._trigger_alert(
                        SecurityEventType.ANOMALOUS_LOGIN,
                        SecurityEventSeverity.LOW,
                        f"Login at unusual hour: {hour}:00",
                        {
                            "user_id": event.user_id,
                            "hour": hour,
                            "event_type": event.event_type.value
                        }
                    )
                    
        except Exception as e:
            logger.debug(f"Time anomaly check failed: {e}")
    
    async def _trigger_alert(
        self,
        alert_type: SecurityEventType,
        severity: SecurityEventSeverity,
        message: str,
        details: Dict[str, Any]
    ):
        """Trigger a security alert.
        
        Args:
            alert_type: Type of security alert
            severity: Alert severity
            message: Alert message
            details: Additional alert details
        """
        try:
            alert = SecurityEvent(
                event_type=alert_type,
                severity=severity,
                details={
                    "alert_message": message,
                    **details
                }
            )
            
            # Log the alert
            logger.warning(
                f"Security alert: {message}",
                alert_type=alert_type.value,
                severity=severity.value,
                **details
            )
            
            # Store alert
            if self.cache:
                alert_key = f"security_alert:{alert.event_id}"
                await self.cache.set(alert_key, alert.to_dict(), timedelta(days=30))
            
            # Call alert handlers
            for handler in self._alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to trigger security alert: {e}")
    
    async def get_security_summary(self, time_window: timedelta = None) -> Dict[str, Any]:
        """Get security event summary.
        
        Args:
            time_window: Time window for summary (default: last 24 hours)
            
        Returns:
            Security summary dictionary
        """
        if not self.cache:
            return {"error": "Cache service not available"}
        
        time_window = time_window or timedelta(hours=24)
        
        try:
            # Get events from the specified time window
            end_time = datetime.now(UTC)
            start_time = end_time - time_window
            
            summary = {
                "time_window": str(time_window),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "event_counts": {},
                "alerts": [],
                "top_ips": [],
                "top_users": []
            }
            
            # Get event counts by type
            for event_type in SecurityEventType:
                count_key = f"event_count:{event_type.value}:day"
                count = await self.cache.get(count_key) or 0
                summary["event_counts"][event_type.value] = count
            
            # Get recent alerts
            # This would require more sophisticated querying in a real implementation
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get security summary: {e}")
            return {"error": str(e)}


# Singleton instance
_security_monitor: SecurityMonitor | None = None


async def get_security_monitor():
    """Get security monitor instance."""
    global _security_monitor
    
    if _security_monitor is None:
        try:
            from chatter.services.cache import get_cache_service
            cache_service = await get_cache_service()
            _security_monitor = SecurityMonitor(cache_service)
        except Exception as e:
            logger.warning(f"Failed to initialize security monitor with cache: {e}")
            _security_monitor = SecurityMonitor()
    
    return _security_monitor


# Convenience functions for logging common events
async def log_login_success(user_id: str, ip_address: str, user_agent: str = None):
    """Log successful login event."""
    monitor = await get_security_monitor()
    event = SecurityEvent(
        event_type=SecurityEventType.LOGIN_SUCCESS,
        severity=SecurityEventSeverity.LOW,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    await monitor.log_security_event(event)


async def log_login_failure(identifier: str, ip_address: str, user_agent: str = None):
    """Log failed login event."""
    monitor = await get_security_monitor()
    event = SecurityEvent(
        event_type=SecurityEventType.LOGIN_FAILURE,
        severity=SecurityEventSeverity.MEDIUM,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"identifier": identifier}
    )
    await monitor.log_security_event(event)


async def log_password_change(user_id: str, ip_address: str = None):
    """Log password change event."""
    monitor = await get_security_monitor()
    event = SecurityEvent(
        event_type=SecurityEventType.PASSWORD_CHANGED,
        severity=SecurityEventSeverity.MEDIUM,
        user_id=user_id,
        ip_address=ip_address
    )
    await monitor.log_security_event(event)


async def log_api_key_created(user_id: str, key_name: str, ip_address: str = None):
    """Log API key creation event."""
    monitor = await get_security_monitor()
    event = SecurityEvent(
        event_type=SecurityEventType.API_KEY_CREATED,
        severity=SecurityEventSeverity.MEDIUM,
        user_id=user_id,
        ip_address=ip_address,
        details={"key_name": key_name}
    )
    await monitor.log_security_event(event)


async def log_account_locked(user_id: str, ip_address: str, reason: str):
    """Log account lockout event."""
    monitor = await get_security_monitor()
    event = SecurityEvent(
        event_type=SecurityEventType.ACCOUNT_LOCKED,
        severity=SecurityEventSeverity.HIGH,
        user_id=user_id,
        ip_address=ip_address,
        details={"reason": reason}
    )
    await monitor.log_security_event(event)