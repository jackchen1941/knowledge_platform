#!/usr/bin/env python3
"""
Comprehensive Security Test Suite

Test all security features including:
- Authentication security
- Input validation
- Rate limiting
- Brute force protection
- SQL injection prevention
- XSS protection
- CSRF protection
- Session security
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class SecurityTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "details": []
        }
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results["details"].append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if passed:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
    
    def log_warning(self, test_name: str, details: str = ""):
        """Log warning."""
        print(f"⚠️  WARN {test_name}")
        if details:
            print(f"   {details}")
        self.test_results["warnings"] += 1

    async def test_authentication_security(self):
        """Test authentication security features."""
        print("\n🔐 Authentication Security Tests")
        print("-" * 40)
        
        # Test 1: Password strength validation
        weak_passwords = ["123", "password", "abc123", "qwerty"]
        for password in weak_passwords:
            register_data = {
                "username": f"weaktest_{int(time.time())}",
                "email": f"weaktest_{int(time.time())}@test.com",
                "password": password,
                "full_name": "Weak Password Test"
            }
            
            try:
                async with self.session.post(
                    f"{BASE_URL}/api/v1/auth/register",
                    json=register_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 400:
                        self.log_test(
                            f"Weak password rejection ({password})",
                            True,
                            "Weak password correctly rejected"
                        )
                    else:
                        self.log_test(
                            f"Weak password rejection ({password})",
                            False,
                            f"Weak password accepted: {response.status}"
                        )
            except Exception as e:
                self.log_test(
                    f"Weak password test ({password})",
                    False,
                    f"Test failed with exception: {e}"
                )
        
        # Test 2: SQL injection in login
        sql_injection_attempts = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
            "admin' UNION SELECT * FROM users --",
            "' OR 1=1 --"
        ]
        
        for injection in sql_injection_attempts:
            login_data = {
                "email": injection,
                "password": "anypassword"
            }
            
            try:
                async with self.session.post(
                    f"{BASE_URL}/api/v1/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status in [400, 401]:
                        self.log_test(
                            f"SQL injection prevention (login)",
                            True,
                            f"Injection attempt blocked: {injection[:20]}..."
                        )
                    else:
                        self.log_test(
                            f"SQL injection prevention (login)",
                            False,
                            f"Injection attempt not blocked: {response.status}"
                        )
            except Exception as e:
                self.log_test(
                    f"SQL injection test (login)",
                    False,
                    f"Test failed: {e}"
                )
        
        # Test 3: Brute force protection
        print("\n   Testing brute force protection...")
        failed_attempts = 0
        for i in range(10):  # Try 10 failed logins
            login_data = {
                "email": "nonexistent@test.com",
                "password": f"wrongpassword{i}"
            }
            
            try:
                async with self.session.post(
                    f"{BASE_URL}/api/v1/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 401:
                        failed_attempts += 1
                    elif response.status == 429:  # Rate limited
                        self.log_test(
                            "Brute force protection",
                            True,
                            f"Account locked after {failed_attempts} attempts"
                        )
                        break
            except Exception:
                pass
        else:
            self.log_warning(
                "Brute force protection",
                "No rate limiting detected after 10 failed attempts"
            )

    async def test_input_validation(self):
        """Test input validation and sanitization."""
        print("\n🛡️  Input Validation Tests")
        print("-" * 40)
        
        # First, create a valid user for testing
        register_data = {
            "username": f"sectest_{int(time.time())}",
            "email": f"sectest_{int(time.time())}@test.com",
            "password": "securepass123",
            "full_name": "Security Test User"
        }
        
        async with self.session.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=register_data
        ) as response:
            if response.status != 200:
                print("Failed to create test user for input validation tests")
                return
        
        # Login to get token
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        async with self.session.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                token = result['access_token']
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            else:
                print("Failed to login for input validation tests")
                return
        
        # Test XSS in knowledge creation
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "onload=alert('XSS')"
        ]
        
        for payload in xss_payloads:
            knowledge_data = {
                "title": f"XSS Test: {payload}",
                "content": f"Content with XSS: {payload}",
                "content_type": "markdown"
            }
            
            try:
                async with self.session.post(
                    f"{BASE_URL}/api/v1/knowledge/",
                    json=knowledge_data,
                    headers=headers
                ) as response:
                    if response.status == 400:
                        self.log_test(
                            f"XSS prevention",
                            True,
                            f"XSS payload blocked: {payload[:30]}..."
                        )
                    elif response.status == 200:
                        # Check if payload was sanitized
                        result = await response.json()
                        if payload not in result.get('title', '') and payload not in result.get('content', ''):
                            self.log_test(
                                f"XSS sanitization",
                                True,
                                f"XSS payload sanitized: {payload[:30]}..."
                            )
                        else:
                            self.log_test(
                                f"XSS prevention",
                                False,
                                f"XSS payload not blocked or sanitized"
                            )
            except Exception as e:
                self.log_test(
                    f"XSS test",
                    False,
                    f"Test failed: {e}"
                )
        
        # Test SQL injection in search
        sql_payloads = [
            "'; DROP TABLE knowledge_items; --",
            "' UNION SELECT * FROM users --",
            "' OR '1'='1",
            "admin'/**/OR/**/1=1--"
        ]
        
        for payload in sql_payloads:
            try:
                async with self.session.get(
                    f"{BASE_URL}/api/v1/search/?q={payload}",
                    headers=headers
                ) as response:
                    if response.status == 400:
                        self.log_test(
                            f"SQL injection prevention (search)",
                            True,
                            f"SQL injection blocked: {payload[:30]}..."
                        )
                    elif response.status == 200:
                        # Check if results are normal (not exposing sensitive data)
                        result = await response.json()
                        if 'results' in result and len(result['results']) < 100:  # Normal result
                            self.log_test(
                                f"SQL injection handling (search)",
                                True,
                                f"SQL injection handled safely"
                            )
                        else:
                            self.log_test(
                                f"SQL injection prevention (search)",
                                False,
                                f"Suspicious large result set"
                            )
            except Exception as e:
                self.log_test(
                    f"SQL injection test (search)",
                    False,
                    f"Test failed: {e}"
                )

    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        print("\n⏱️  Rate Limiting Tests")
        print("-" * 40)
        
        # Test API rate limiting
        start_time = time.time()
        successful_requests = 0
        rate_limited = False
        
        for i in range(50):  # Try 50 requests quickly
            try:
                async with self.session.get(f"{BASE_URL}/status") as response:
                    if response.status == 200:
                        successful_requests += 1
                    elif response.status == 429:
                        rate_limited = True
                        break
            except Exception:
                pass
        
        elapsed_time = time.time() - start_time
        
        if rate_limited:
            self.log_test(
                "API rate limiting",
                True,
                f"Rate limited after {successful_requests} requests in {elapsed_time:.2f}s"
            )
        elif successful_requests == 50 and elapsed_time < 2:
            self.log_warning(
                "API rate limiting",
                f"No rate limiting detected for {successful_requests} requests in {elapsed_time:.2f}s"
            )
        else:
            self.log_test(
                "API rate limiting",
                True,
                f"Reasonable performance: {successful_requests} requests in {elapsed_time:.2f}s"
            )

    async def test_session_security(self):
        """Test session security features."""
        print("\n🔑 Session Security Tests")
        print("-" * 40)
        
        # Test JWT token validation
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "Bearer malformed",
            "totally-not-a-jwt-token"
        ]
        
        for token in invalid_tokens:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            try:
                async with self.session.get(
                    f"{BASE_URL}/api/v1/me",
                    headers=headers
                ) as response:
                    if response.status == 401:
                        self.log_test(
                            f"Invalid token rejection",
                            True,
                            f"Invalid token correctly rejected"
                        )
                    else:
                        self.log_test(
                            f"Invalid token rejection",
                            False,
                            f"Invalid token accepted: {response.status}"
                        )
            except Exception as e:
                self.log_test(
                    f"Token validation test",
                    False,
                    f"Test failed: {e}"
                )

    async def test_security_headers(self):
        """Test security headers."""
        print("\n🛡️  Security Headers Tests")
        print("-" * 40)
        
        expected_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block"
        }
        
        try:
            async with self.session.get(f"{BASE_URL}/status") as response:
                headers = response.headers
                
                for header, expected_value in expected_headers.items():
                    if header in headers:
                        if headers[header] == expected_value:
                            self.log_test(
                                f"Security header: {header}",
                                True,
                                f"Correct value: {expected_value}"
                            )
                        else:
                            self.log_test(
                                f"Security header: {header}",
                                False,
                                f"Wrong value: {headers[header]} (expected: {expected_value})"
                            )
                    else:
                        self.log_test(
                            f"Security header: {header}",
                            False,
                            f"Header missing"
                        )
        except Exception as e:
            self.log_test(
                "Security headers test",
                False,
                f"Test failed: {e}"
            )

    async def test_data_exposure(self):
        """Test for data exposure vulnerabilities."""
        print("\n🔍 Data Exposure Tests")
        print("-" * 40)
        
        # Test error message information disclosure
        try:
            async with self.session.get(f"{BASE_URL}/api/v1/knowledge/nonexistent-id") as response:
                if response.status == 404:
                    result = await response.json()
                    error_detail = result.get('detail', '')
                    
                    # Check if error message reveals sensitive information
                    sensitive_keywords = ['database', 'sql', 'table', 'column', 'query', 'exception']
                    has_sensitive_info = any(keyword in error_detail.lower() for keyword in sensitive_keywords)
                    
                    if has_sensitive_info:
                        self.log_test(
                            "Error message disclosure",
                            False,
                            f"Error message may reveal sensitive info: {error_detail[:100]}"
                        )
                    else:
                        self.log_test(
                            "Error message disclosure",
                            True,
                            "Error messages don't reveal sensitive information"
                        )
        except Exception as e:
            self.log_test(
                "Data exposure test",
                False,
                f"Test failed: {e}"
            )
        
        # Test API documentation exposure
        try:
            async with self.session.get(f"{BASE_URL}/docs") as response:
                if response.status == 200:
                    self.log_warning(
                        "API documentation exposure",
                        "API documentation is publicly accessible"
                    )
                else:
                    self.log_test(
                        "API documentation protection",
                        True,
                        "API documentation is not publicly accessible"
                    )
        except Exception:
            self.log_test(
                "API documentation protection",
                True,
                "API documentation is not accessible"
            )

    async def run_all_tests(self):
        """Run all security tests."""
        print("🔒 Comprehensive Security Test Suite")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            await self.test_authentication_security()
            await self.test_input_validation()
            await self.test_rate_limiting()
            await self.test_session_security()
            await self.test_security_headers()
            await self.test_data_exposure()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔒 Security Test Summary")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⚠️  Warnings: {self.test_results['warnings']}")
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Security recommendations
        print("\n🛡️  Security Recommendations:")
        if self.test_results['failed'] > 0:
            print("- Address failed security tests immediately")
        if self.test_results['warnings'] > 0:
            print("- Review warnings and implement additional security measures")
        print("- Regularly run security tests")
        print("- Keep dependencies updated")
        print("- Implement security monitoring")
        print("- Consider penetration testing")
        
        return self.test_results


async def main():
    """Run security tests."""
    tester = SecurityTester()
    results = await tester.run_all_tests()
    
    # Save results to file
    with open('security_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: security_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())