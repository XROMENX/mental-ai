import requests
import unittest
import json
import uuid
import time
from datetime import datetime

class PersianMentalHealthAPITest(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://aae197da-d3d8-4951-8d0c-e6ef8f61190f.preview.emergentagent.com"
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
        
    def test_01_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{self.base_url}/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        print("✅ Health check endpoint is working")
        
    def test_02_register_user(self):
        """Test user registration"""
        response = requests.post(
            f"{self.base_url}/api/register",
            json=self.test_user
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_email)
        self.token = data["access_token"]
        self.user_id = data["user"]["user_id"]
        print(f"✅ User registration successful with email: {self.test_email}")
        
    def test_03_login_user(self):
        """Test user login"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        response = requests.post(
            f"{self.base_url}/api/login",
            json=login_data
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.token = data["access_token"]
        print("✅ User login successful")
        
    def test_04_get_profile(self):
        """Test getting user profile"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/api/profile",
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.test_email)
        print("✅ Profile retrieval successful")
        
    def test_05_submit_dass21(self):
        """Test submitting DASS-21 assessment"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Generate random responses for all 21 questions (0-3 scale)
        responses = {i: i % 4 for i in range(1, 22)}
        
        response = requests.post(
            f"{self.base_url}/api/submit-dass21",
            json={"responses": responses},
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that all required fields are in the response
        required_fields = [
            "depression_score", "anxiety_score", "stress_score",
            "depression_level", "anxiety_level", "stress_level",
            "ai_analysis", "recommendations"
        ]
        for field in required_fields:
            self.assertIn(field, data)
            
        print("✅ DASS-21 submission successful")
        
    def test_06_get_assessments(self):
        """Test getting user assessments"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/api/assessments",
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("assessment_id", data[0])
            self.assertIn("results", data[0])
        print("✅ Assessments retrieval successful")
        
    def test_07_invalid_login(self):
        """Test invalid login credentials"""
        login_data = {
            "email": self.test_email,
            "password": "WrongPassword123!"
        }
        response = requests.post(
            f"{self.base_url}/api/login",
            json=login_data
        )
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid login credentials properly rejected")
        
    def test_08_registration_validation(self):
        """Test registration validation"""
        # Test without consent
        invalid_user = self.test_user.copy()
        invalid_user["email"] = f"test_{uuid.uuid4().hex[:8]}@example.com"
        invalid_user["consentGiven"] = False
        
        response = requests.post(
            f"{self.base_url}/api/register",
            json=invalid_user
        )
        self.assertEqual(response.status_code, 400)
        
        # Test with mismatched passwords
        invalid_user = self.test_user.copy()
        invalid_user["email"] = f"test_{uuid.uuid4().hex[:8]}@example.com"
        invalid_user["confirmPassword"] = "DifferentPassword123!"
        
        response = requests.post(
            f"{self.base_url}/api/register",
            json=invalid_user
        )
        self.assertEqual(response.status_code, 400)
        
        print("✅ Registration validation working correctly")
        
    def test_09_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        # Try to access profile without token
        response = requests.get(f"{self.base_url}/api/profile")
        self.assertNotEqual(response.status_code, 200)
        
        # Try to submit DASS-21 without token
        responses = {i: i % 4 for i in range(1, 22)}
        response = requests.post(
            f"{self.base_url}/api/submit-dass21",
            json={"responses": responses}
        )
        self.assertNotEqual(response.status_code, 200)
        
        print("✅ Unauthorized access properly rejected")

def run_tests():
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add tests in order
    test_cases = [
        PersianMentalHealthAPITest('test_01_health_check'),
        PersianMentalHealthAPITest('test_02_register_user'),
        PersianMentalHealthAPITest('test_03_login_user'),
        PersianMentalHealthAPITest('test_04_get_profile'),
        PersianMentalHealthAPITest('test_05_submit_dass21'),
        PersianMentalHealthAPITest('test_06_get_assessments'),
        PersianMentalHealthAPITest('test_07_invalid_login'),
        PersianMentalHealthAPITest('test_08_registration_validation'),
        PersianMentalHealthAPITest('test_09_unauthorized_access')
    ]
    
    for test_case in test_cases:
        suite.addTest(test_case)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    print("🧪 Starting Persian Mental Health API Tests")
    print(f"🔗 Testing API at: https://aae197da-d3d8-4951-8d0c-e6ef8f61190f.preview.emergentagent.com")
    print("=" * 70)
    run_tests()
