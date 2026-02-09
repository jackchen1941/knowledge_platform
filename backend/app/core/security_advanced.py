"""
Advanced Security Module

Comprehensive security features including:
- Rate limiting with Redis
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Security headers
- Audit logging
- Brute force protection
- Session management
"""

import hashlib
import hmac
import re
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from ipaddress import ip_address, ip_network
import json

from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
import redis

# Redis connection for rate limiting and session management
redis_client = None

def get_redis_client():
    """获取Redis客户端，如果不可用则返回None"""
    global redis_client
    if redis_client is None:
        try:
            from app.core.config_auto import get_auto_config
            config = get_auto_config()
            redis_config = config.get_redis_config()
            
            if redis_config:
                redis_client = redis.Redis.from_url(redis_config["url"], decode_responses=True)
                # 测试连接
                redis_client.ping()
                logger.info("Redis连接成功 / Redis connected successfully")
            else:
                logger.info("Redis已禁用，使用内存存储 / Redis disabled, using in-memory storage")
                return None
        except Exception as e:
            logger.warning(f"Redis连接失败，使用内存存储: {e} / Redis connection failed, using in-memory storage: {e}")
            redis_client = None
    
    return redis_client


class SecurityConfig:
    """Security configuration constants."""
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_BURST = 10   # burst allowance
    
    # Brute force protection
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_DURATION = 300  # 5 minutes
    
    # Session management
    SESSION_TIMEOUT = 3600  # 1 hour
    MAX_SESSIONS_PER_USER = 5
    
    # Input validation
    MAX_INPUT_LENGTH = 10000
    ALLOWED_HTML_TAGS = {'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # Blocked IP patterns
    BLOCKED_IP_RANGES = [
        "10.0.0.0/8",      # Private networks
        "172.16.0.0/12",
        "192.168.0.0/16",
    ]


class InputValidator:
    """Advanced input validation and sanitization."""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)",
        r"(\bxp_\w+|\bsp_\w+)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
        r"..%2f",
        r"..%5c",
    ]
    
    @classmethod
    def validate_sql_injection(cls, input_str: str) -> bool:
        """Check for SQL injection patterns."""
        if not input_str:
            return True
            
        input_lower = input_str.lower()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected: {pattern}")
                return False
        return True
    
    @classmethod
    def validate_xss(cls, input_str: str) -> bool:
        """Check for XSS patterns."""
        if not input_str:
            return True
            
        input_lower = input_str.lower()
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                logger.warning(f"XSS attempt detected: {pattern}")
                return False
        return True
    
    @classmethod
    def validate_path_traversal(cls, input_str: str) -> bool:
        """Check for path traversal patterns."""
        if not input_str:
            return True
            
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                logger.warning(f"Path traversal attempt detected: {pattern}")
                return False
        return True
    
    @classmethod
    def sanitize_input(cls, input_str: str, max_length: int = None) -> str:
        """Sanitize user input."""
        if not input_str:
            return ""
        
        # Limit length
        if max_length and len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        # Remove null bytes
        input_str = input_str.replace('\x00', '')
        
        # Normalize whitespace
        input_str = re.sub(r'\s+', ' ', input_str).strip()
        
        return input_str
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_username(cls, username: str) -> bool:
        """Validate username format."""
        # Only alphanumeric, underscore, hyphen, 3-30 characters
        pattern = r'^[a-zA-Z0-9_-]{3,30}$'
        return bool(re.match(pattern, username))


class RateLimiter:
    """Advanced rate limiting with Redis backend."""
    
    def __init__(self):
        self.memory_store = {}  # Fallback for when Redis is not available
    
    def _get_key(self, identifier: str, endpoint: str = "global") -> str:
        """Generate rate limit key."""
        return f"rate_limit:{endpoint}:{identifier}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def is_allowed(
        self, 
        request: Request, 
        identifier: str = None,
        endpoint: str = "global",
        max_requests: int = None,
        window_seconds: int = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed under rate limits."""
        
        if not identifier:
            identifier = self._get_client_ip(request)
        
        max_requests = max_requests or SecurityConfig.RATE_LIMIT_REQUESTS
        window_seconds = window_seconds or SecurityConfig.RATE_LIMIT_WINDOW
        
        key = self._get_key(identifier, endpoint)
        now = int(time.time())
        window_start = now - window_seconds
        
        redis_client = get_redis_client()
        if redis_client:
            try:
                # Use Redis sliding window
                pipe = redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(now): now})
                pipe.expire(key, window_seconds)
                results = pipe.execute()
                
                current_requests = results[1]
                
                return current_requests < max_requests, {
                    "allowed": current_requests < max_requests,
                    "current_requests": current_requests,
                    "max_requests": max_requests,
                    "window_seconds": window_seconds,
                    "reset_time": now + window_seconds
                }
            except Exception as e:
                logger.error(f"Redis rate limiting error: {e}")
                # Fall through to memory-based limiting
        
        # Memory-based fallback
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Clean old entries
        self.memory_store[key] = [
            timestamp for timestamp in self.memory_store[key]
            if timestamp > window_start
        ]
        
        current_requests = len(self.memory_store[key])
        
        if current_requests < max_requests:
            self.memory_store[key].append(now)
            return True, {
                "allowed": True,
                "current_requests": current_requests + 1,
                "max_requests": max_requests,
                "window_seconds": window_seconds,
                "reset_time": now + window_seconds
            }
        
        return False, {
            "allowed": False,
            "current_requests": current_requests,
            "max_requests": max_requests,
            "window_seconds": window_seconds,
            "reset_time": now + window_seconds
        }


class BruteForceProtection:
    """Brute force attack protection."""
    
    def __init__(self):
        self.memory_store = {}
    
    def _get_key(self, identifier: str, action: str = "login") -> str:
        """Generate brute force protection key."""
        return f"brute_force:{action}:{identifier}"
    
    async def record_attempt(
        self, 
        identifier: str, 
        success: bool, 
        action: str = "login"
    ) -> None:
        """Record login attempt."""
        key = self._get_key(identifier, action)
        now = int(time.time())
        
        redis_client = get_redis_client()
        if redis_client:
            try:
                if success:
                    # Clear failed attempts on success
                    redis_client.delete(key)
                else:
                    # Increment failed attempts
                    pipe = redis_client.pipeline()
                    pipe.zadd(key, {str(now): now})
                    pipe.expire(key, SecurityConfig.LOGIN_LOCKOUT_DURATION)
                    pipe.execute()
                return
            except Exception as e:
                logger.error(f"Redis brute force protection error: {e}")
        
        # Memory fallback
        if success:
            self.memory_store.pop(key, None)
        else:
            if key not in self.memory_store:
                self.memory_store[key] = []
            self.memory_store[key].append(now)
            
            # Clean old attempts
            cutoff = now - SecurityConfig.LOGIN_LOCKOUT_DURATION
            self.memory_store[key] = [
                timestamp for timestamp in self.memory_store[key]
                if timestamp > cutoff
            ]
    
    async def is_blocked(self, identifier: str, action: str = "login") -> Tuple[bool, Dict[str, Any]]:
        """Check if identifier is blocked due to too many failed attempts."""
        key = self._get_key(identifier, action)
        now = int(time.time())
        cutoff = now - SecurityConfig.LOGIN_LOCKOUT_DURATION
        
        redis_client = get_redis_client()
        if redis_client:
            try:
                # Clean old attempts and count current ones
                pipe = redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, cutoff)
                pipe.zcard(key)
                results = pipe.execute()
                
                failed_attempts = results[1]
                
                is_blocked = failed_attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS
                
                return is_blocked, {
                    "blocked": is_blocked,
                    "failed_attempts": failed_attempts,
                    "max_attempts": SecurityConfig.MAX_LOGIN_ATTEMPTS,
                    "lockout_duration": SecurityConfig.LOGIN_LOCKOUT_DURATION,
                    "unblock_time": now + SecurityConfig.LOGIN_LOCKOUT_DURATION if is_blocked else None
                }
            except Exception as e:
                logger.error(f"Redis brute force check error: {e}")
        
        # Memory fallback
        attempts = self.memory_store.get(key, [])
        recent_attempts = [t for t in attempts if t > cutoff]
        
        is_blocked = len(recent_attempts) >= SecurityConfig.MAX_LOGIN_ATTEMPTS
        
        return is_blocked, {
            "blocked": is_blocked,
            "failed_attempts": len(recent_attempts),
            "max_attempts": SecurityConfig.MAX_LOGIN_ATTEMPTS,
            "lockout_duration": SecurityConfig.LOGIN_LOCKOUT_DURATION,
            "unblock_time": now + SecurityConfig.LOGIN_LOCKOUT_DURATION if is_blocked else None
        }


class SecurityAuditor:
    """Security event auditing and logging."""
    
    @staticmethod
    def log_security_event(
        event_type: str,
        user_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        details: Dict[str, Any] = None,
        severity: str = "INFO"
    ) -> None:
        """Log security event."""
        
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            "severity": severity
        }
        
        # Log to structured logger
        logger.bind(security_event=True).log(
            severity, 
            f"Security Event: {event_type}",
            **event_data
        )
        
        # Store in Redis for analysis (if available)
        redis_client = get_redis_client()
        if redis_client:
            try:
                key = f"security_events:{datetime.utcnow().strftime('%Y-%m-%d')}"
                redis_client.lpush(key, json.dumps(event_data))
                redis_client.expire(key, 86400 * 30)  # Keep for 30 days
            except Exception as e:
                logger.error(f"Failed to store security event: {e}")
    
    @staticmethod
    def log_authentication_attempt(
        user_id: str = None,
        email: str = None,
        ip_address: str = None,
        user_agent: str = None,
        success: bool = False,
        failure_reason: str = None
    ) -> None:
        """Log authentication attempt."""
        
        SecurityAuditor.log_security_event(
            event_type="AUTHENTICATION_ATTEMPT",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "email": email,
                "success": success,
                "failure_reason": failure_reason
            },
            severity="INFO" if success else "WARNING"
        )
    
    @staticmethod
    def log_suspicious_activity(
        activity_type: str,
        user_id: str = None,
        ip_address: str = None,
        details: Dict[str, Any] = None
    ) -> None:
        """Log suspicious activity."""
        
        SecurityAuditor.log_security_event(
            event_type="SUSPICIOUS_ACTIVITY",
            user_id=user_id,
            ip_address=ip_address,
            details={
                "activity_type": activity_type,
                **(details or {})
            },
            severity="WARNING"
        )


class IPFilter:
    """IP address filtering and geolocation."""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.blocked_networks = [ip_network(net) for net in SecurityConfig.BLOCKED_IP_RANGES]
    
    def is_blocked_ip(self, ip_str: str) -> bool:
        """Check if IP is blocked."""
        try:
            ip = ip_address(ip_str)
            
            # Check individual blocked IPs
            if ip_str in self.blocked_ips:
                return True
            
            # Check blocked networks
            for network in self.blocked_networks:
                if ip in network:
                    return True
            
            return False
        except ValueError:
            # Invalid IP format
            return True
    
    def block_ip(self, ip_str: str, duration: int = 3600) -> None:
        """Block an IP address."""
        self.blocked_ips.add(ip_str)
        
        redis_client = get_redis_client()
        if redis_client:
            try:
                redis_client.setex(f"blocked_ip:{ip_str}", duration, "1")
            except Exception as e:
                logger.error(f"Failed to store blocked IP: {e}")
    
    def unblock_ip(self, ip_str: str) -> None:
        """Unblock an IP address."""
        self.blocked_ips.discard(ip_str)
        
        redis_client = get_redis_client()
        if redis_client:
            try:
                redis_client.delete(f"blocked_ip:{ip_str}")
            except Exception as e:
                logger.error(f"Failed to remove blocked IP: {e}")


# Global instances
rate_limiter = RateLimiter()
brute_force_protection = BruteForceProtection()
ip_filter = IPFilter()


class SecurityMiddleware:
    """Comprehensive security middleware."""
    
    def __init__(self):
        self.rate_limiter = rate_limiter
        self.brute_force_protection = brute_force_protection
        self.ip_filter = ip_filter
    
    async def __call__(self, request: Request, call_next):
        """Process request through security checks."""
        
        # Get client info
        client_ip = self.rate_limiter._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        # IP filtering
        if self.ip_filter.is_blocked_ip(client_ip):
            SecurityAuditor.log_suspicious_activity(
                "BLOCKED_IP_ACCESS",
                ip_address=client_ip,
                details={"user_agent": user_agent}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Rate limiting
        allowed, rate_info = await self.rate_limiter.is_allowed(request)
        if not allowed:
            SecurityAuditor.log_suspicious_activity(
                "RATE_LIMIT_EXCEEDED",
                ip_address=client_ip,
                details={
                    "user_agent": user_agent,
                    "rate_info": rate_info
                }
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(rate_info["window_seconds"])}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_info["max_requests"])
        response.headers["X-RateLimit-Remaining"] = str(
            rate_info["max_requests"] - rate_info["current_requests"]
        )
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset_time"])
        
        return response


def validate_request_security(request_data: Dict[str, Any]) -> None:
    """Validate request data for security issues."""
    
    for key, value in request_data.items():
        if isinstance(value, str):
            # Check for SQL injection
            if not InputValidator.validate_sql_injection(value):
                SecurityAuditor.log_suspicious_activity(
                    "SQL_INJECTION_ATTEMPT",
                    details={"field": key, "value": value[:100]}
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            # Check for XSS
            if not InputValidator.validate_xss(value):
                SecurityAuditor.log_suspicious_activity(
                    "XSS_ATTEMPT",
                    details={"field": key, "value": value[:100]}
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            # Check for path traversal
            if not InputValidator.validate_path_traversal(value):
                SecurityAuditor.log_suspicious_activity(
                    "PATH_TRAVERSAL_ATTEMPT",
                    details={"field": key, "value": value[:100]}
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )


def generate_csrf_token(user_id: str) -> str:
    """Generate CSRF token for user."""
    from app.core.config_auto import get_auto_config
    config = get_auto_config()
    
    timestamp = str(int(time.time()))
    data = f"{user_id}:{timestamp}"
    signature = hmac.new(
        config.SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{data}:{signature}"


def validate_csrf_token(token: str, user_id: str, max_age: int = 3600) -> bool:
    """Validate CSRF token."""
    try:
        from app.core.config_auto import get_auto_config
        config = get_auto_config()
        
        parts = token.split(":")
        if len(parts) != 3:
            return False
        
        token_user_id, timestamp, signature = parts
        
        # Check user ID
        if token_user_id != user_id:
            return False
        
        # Check age
        token_time = int(timestamp)
        if time.time() - token_time > max_age:
            return False
        
        # Verify signature
        data = f"{token_user_id}:{timestamp}"
        expected_signature = hmac.new(
            config.SECRET_KEY.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except (ValueError, TypeError):
        return False