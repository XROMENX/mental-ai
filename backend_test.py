import sys
import uuid
from datetime import datetime

import os
import requests


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
            "consentGiven": True,
        }
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(
        self, name, method, endpoint, expected_status, data=None, headers=None
    ):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
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
                print(
                    f"❌ Failed - Expected {expected_status}, got {response.status_code}"
                )
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
        success, data = self.run_test("Health Check", "GET", "api/health", 200)
        if success:
            assert data["status"] == "healthy"
            print("✅ Health check endpoint is working")
        return success

    def test_register_user(self):
        """Test user registration"""
        success, data = self.run_test(
            "User Registration", "POST", "api/register", 200, data=self.test_user
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
        login_data = {"email": self.test_email, "password": self.test_password}
        success, data = self.run_test(
            "User Login", "POST", "api/login", 200, data=login_data
        )
        if success:
            assert "access_token" in data
            self.token = data["access_token"]
            print("✅ User login successful")
        return success

    def test_get_profile(self):
        """Test getting user profile"""
        success, data = self.run_test("Get Profile", "GET", "api/profile", 200)
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
            data={"responses": responses},
        )
        if success:
            # Check that all required fields are in the response
            required_fields = [
                "depression_score",
                "anxiety_score",
                "stress_score",
                "depression_level",
                "anxiety_level",
                "stress_level",
                "ai_analysis",
                "recommendations",
            ]
            for field in required_fields:
                assert field in data
            print("✅ DASS-21 submission successful")
        return success

    def test_submit_phq9(self):
        """Test submitting PHQ-9 assessment"""
        # Generate responses for all 9 questions (0-3 scale)
        responses = {i: i % 4 for i in range(1, 10)}

        success, data = self.run_test(
            "Submit PHQ-9",
            "POST",
            "api/submit-phq9",
            200,
            data={"responses": responses},
        )
        if success:
            # Check that all required fields are in the response
            required_fields = [
                "total_score",
                "severity_level",
                "analysis",
                "recommendations",
            ]
            for field in required_fields:
                assert field in data
            print("✅ PHQ-9 submission successful")
        return success

    def test_mood_entry(self):
        """Test saving mood entry"""
        mood_data = {
            "mood_level": 4,  # Good mood
            "note": "Feeling good today, completed a project",
        }

        success, data = self.run_test(
            "Save Mood Entry", "POST", "api/mood-entry", 200, data=mood_data
        )
        if success:
            assert "message" in data
            print("✅ Mood entry saved successfully")
        return success

    def test_get_mood_entries(self):
        """Test getting mood entries"""
        success, data = self.run_test(
            "Get Mood Entries", "GET", "api/mood-entries", 200
        )
        if success:
            assert isinstance(data, list)
            if len(data) > 0:
                assert "mood_level" in data[0]
                assert "date" in data[0]
            print("✅ Mood entries retrieval successful")
        return success

    def test_sleep_entry(self):
        """Test saving sleep entry"""
        sleep_data = {"hours": 7.5, "quality": 4, "note": "Good sleep"}
        success, data = self.run_test(
            "Save Sleep Entry", "POST", "api/sleep-entry", 200, data=sleep_data
        )
        if success:
            assert "message" in data
            print("✅ Sleep entry saved successfully")
        return success

    def test_get_sleep_entries(self):
        """Test getting sleep entries"""
        success, data = self.run_test(
            "Get Sleep Entries", "GET", "api/sleep-entries", 200
        )
        if success:
            assert isinstance(data, list)
            if len(data) > 0:
                assert "hours" in data[0]
                assert "quality" in data[0]
            print("✅ Sleep entries retrieval successful")
        return success

    def test_daily_reflection(self):
        """Test saving daily reflection"""
        ref = {"text": "Feeling productive"}
        success, data = self.run_test(
            "Save Daily Reflection", "POST", "api/daily-reflection", 200, data=ref
        )
        if success:
            assert "message" in data
            print("✅ Daily reflection saved successfully")
        return success

    def test_get_daily_reflections(self):
        """Test getting reflections"""
        success, data = self.run_test(
            "Get Daily Reflections", "GET", "api/daily-reflections", 200
        )
        if success:
            assert isinstance(data, list)
            if len(data) > 0:
                assert "text" in data[0]
            print("✅ Daily reflections retrieval successful")
        return success

    def test_chat_with_bot(self):
        """Test chatting with the bot"""
        # Test different types of messages
        chat_messages = [
            "سلام",  # Greeting
            "من امروز خیلی خوشحالم",  # Happy mood
            "من استرس دارم",  # Stress
            "من نگران امتحانم هستم",  # Anxiety
            "من خوب نخوابیدم",  # Sleep issue
        ]

        all_success = True
        for message in chat_messages:
            success, data = self.run_test(
                f"Chat Message: '{message}'",
                "POST",
                "api/chat",
                200,
                data={"message": message},
            )
            if success:
                assert "response" in data
                print(f"✅ Bot responded to '{message}'")
            else:
                all_success = False

        return all_success

    def test_get_mental_health_plan(self):
        """Test getting mental health plan"""
        success, data = self.run_test(
            "Get Mental Health Plan", "GET", "api/mental-health-plan", 200
        )
        if success:
            assert "daily_habits" in data
            assert "weekly_goals" in data
            assert "emergency_contacts" in data
            print("✅ Mental health plan retrieval successful")
        return success

    def test_get_assessments(self):
        """Test getting user assessments"""
        success, data = self.run_test("Get Assessments", "GET", "api/assessments", 200)
        if success:
            assert isinstance(data, list)
            if len(data) > 0:
                assert "assessment_id" in data[0]
                assert "results" in data[0]
            print("✅ Assessments retrieval successful")
        return success

    def test_invalid_login(self):
        """Test invalid login credentials"""
        login_data = {"email": self.test_email, "password": "WrongPassword123!"}
        success, _ = self.run_test(
            "Invalid Login", "POST", "api/login", 400, data=login_data
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
            data=invalid_user,
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
            data=invalid_user,
        )

        if success1 and success2:
            print("✅ Registration validation working correctly")
        return success1 and success2

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        # Try to access profile without token
        success1, _ = self.run_test(
            "Unauthorized Profile Access", "GET", "api/profile", 403, headers={}
        )

        # Try to submit DASS-21 without token
        responses = {i: i % 4 for i in range(1, 22)}
        success2, _ = self.run_test(
            "Unauthorized DASS-21 Submission",
            "POST",
            "api/submit-dass21",
            404,
            data={"responses": responses},
            headers={},
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

            # Feature tests
            self.test_submit_dass21()
            self.test_submit_phq9()
            self.test_mood_entry()
            self.test_get_mood_entries()
            self.test_sleep_entry()
            self.test_get_sleep_entries()
            self.test_daily_reflection()
            self.test_get_daily_reflections()
            self.test_chat_with_bot()
            self.test_get_mental_health_plan()
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
    base_url = os.getenv("API_BASE_URL", "http://localhost:8001")
    tester = PersianMentalHealthAPITester(base_url)
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
