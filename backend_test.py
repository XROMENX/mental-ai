import requests
import sys
import uuid
from datetime import datetime

class PersianMentalHealthAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        # Generate unique email for testing
        self.test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "TestPassword123!"
        self.test_user = {
            "email": self.test_email,
            "password": self.test_password,
            "confirmPassword": self.test_password,
            "fullName": "Test User",
            "age": 25,
            "studentLevel": "master",
            "consentGiven": True
        }
        self.tests_run = 0
        self.tests_passed = 0
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
    
    def test_health_check(self):
        """Test the health check endpoint"""
        success, data = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        if success:
            assert data["status"] == "healthy"
            print("✅ Health check endpoint is working")
        return success
    
    def test_register_user(self):
        """Test user registration"""
        success, data = self.run_test(
            "User Registration",
            "POST",
            "api/register",
            200,
            data=self.test_user
        )
        if success:
            assert "access_token" in data
            assert "user" in data
            assert data["user"]["email"] == self.test_email
            self.token = data["access_token"]
            self.user_id = data["user"]["user_id"]
            print(f"✅ User registration successful with email: {self.test_email}")
        return success
    
    def test_login_user(self):
        """Test user login"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        success, data = self.run_test(
            "User Login",
            "POST",
            "api/login",
            200,
            data=login_data
        )
        if success:
            assert "access_token" in data
            self.token = data["access_token"]
            print("✅ User login successful")
        return success
    
    def test_get_profile(self):
        """Test getting user profile"""
        success, data = self.run_test(
            "Get Profile",
            "GET",
            "api/profile",
            200
        )
        if success:
            assert data["email"] == self.test_email
            print("✅ Profile retrieval successful")
        return success
    
    def test_submit_dass21(self):
        """Test submitting DASS-21 assessment"""
        # Generate responses for all 21 questions (0-3 scale)
        responses = {i: i % 4 for i in range(1, 22)}
        
        success, data = self.run_test(
            "Submit DASS-21",
            "POST",
            "api/submit-dass21",
            200,
            data={"responses": responses}
        )
        if success:
            # Check that all required fields are in the response
            required_fields = [
                "depression_score", "anxiety_score", "stress_score",
                "depression_level", "anxiety_level", "stress_level",
                "ai_analysis", "recommendations"
            ]
            for field in required_fields:
                assert field in data
            print("✅ DASS-21 submission successful")
        return success
    
    def test_get_assessments(self):
        """Test getting user assessments"""
        success, data = self.run_test(
            "Get Assessments",
            "GET",
            "api/assessments",
            200
        )
        if success:
            assert isinstance(data, list)
            if len(data) > 0:
                assert "assessment_id" in data[0]
                assert "results" in data[0]
            print("✅ Assessments retrieval successful")
        return success
    
    def test_invalid_login(self):
        """Test invalid login credentials"""
        login_data = {
            "email": self.test_email,
            "password": "WrongPassword123!"
        }
        success, _ = self.run_test(
            "Invalid Login",
            "POST",
            "api/login",
            400,
            data=login_data
        )
        if success:
            print("✅ Invalid login credentials properly rejected")
        return success
    
    def test_registration_validation(self):
        """Test registration validation"""
        # Test without consent
        invalid_user = self.test_user.copy()
        invalid_user["email"] = f"test_{uuid.uuid4().hex[:8]}@example.com"
        invalid_user["consentGiven"] = False
        
        success1, _ = self.run_test(
            "Registration without Consent",
            "POST",
            "api/register",
            400,
            data=invalid_user
        )
        
        # Test with mismatched passwords
        invalid_user = self.test_user.copy()
        invalid_user["email"] = f"test_{uuid.uuid4().hex[:8]}@example.com"
        invalid_user["confirmPassword"] = "DifferentPassword123!"
        
        success2, _ = self.run_test(
            "Registration with Mismatched Passwords",
            "POST",
            "api/register",
            400,
            data=invalid_user
        )
        
        if success1 and success2:
            print("✅ Registration validation working correctly")
        return success1 and success2
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        # Try to access profile without token
        success1, _ = self.run_test(
            "Unauthorized Profile Access",
            "GET",
            "api/profile",
            401,
            headers={}
        )
        
        # Try to submit DASS-21 without token
        responses = {i: i % 4 for i in range(1, 22)}
        success2, _ = self.run_test(
            "Unauthorized DASS-21 Submission",
            "POST",
            "api/submit-dass21",
            401,
            data={"responses": responses},
            headers={}
        )
        
        if success1 and success2:
            print("✅ Unauthorized access properly rejected")
        return success1 and success2
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Starting Persian Mental Health API Tests")
        print(f"🔗 Testing API at: {self.base_url}")
        print("=" * 70)
        
        # Run tests in order
        self.test_health_check()
        
        # Registration and authentication flow
        if self.test_register_user():
            self.test_login_user()
            self.test_get_profile()
            
            # DASS-21 assessment flow
            self.test_submit_dass21()
            self.test_get_assessments()
        
        # Error handling tests
        self.test_invalid_login()
        self.test_registration_validation()
        self.test_unauthorized_access()
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    base_url = "https://aae197da-d3d8-4951-8d0c-e6ef8f61190f.preview.emergentagent.com"
    tester = PersianMentalHealthAPITester(base_url)
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
