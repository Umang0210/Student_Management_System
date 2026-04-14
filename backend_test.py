#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class StudentManagementAPITester:
    def __init__(self, base_url="https://student-hub-686.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_credentials = {
            "email": "admin@example.com",
            "password": "admin123"
        }

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def test_auth_login(self):
        """Test admin login functionality"""
        print("\n🔐 Testing Authentication...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == self.admin_credentials["email"]:
                    return self.log_test("Admin Login", True, f"- User: {data.get('name', 'Admin')}")
                else:
                    return self.log_test("Admin Login", False, "- Invalid response data")
            else:
                return self.log_test("Admin Login", False, f"- Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Admin Login", False, f"- Error: {str(e)}")

    def test_auth_me(self):
        """Test getting current user info"""
        try:
            response = self.session.get(f"{self.base_url}/api/auth/me", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == self.admin_credentials["email"]:
                    return self.log_test("Get Current User", True, f"- Role: {data.get('role', 'N/A')}")
                else:
                    return self.log_test("Get Current User", False, "- Invalid user data")
            else:
                return self.log_test("Get Current User", False, f"- Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Get Current User", False, f"- Error: {str(e)}")

    def test_create_student(self, student_data):
        """Test creating a new student"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/students",
                json=student_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == student_data["email"]:
                    return self.log_test("Create Student", True, f"- ID: {data.get('id')}, Name: {data.get('name')}"), data.get("id")
                else:
                    return self.log_test("Create Student", False, "- Invalid response data"), None
            else:
                return self.log_test("Create Student", False, f"- Status: {response.status_code}, Response: {response.text}"), None
                
        except Exception as e:
            return self.log_test("Create Student", False, f"- Error: {str(e)}"), None

    def test_get_students(self, search=None, status=None, page=1, limit=10):
        """Test getting students list with optional filters"""
        try:
            params = {"page": page, "limit": limit}
            if search:
                params["search"] = search
            if status:
                params["status"] = status
                
            response = self.session.get(
                f"{self.base_url}/api/students",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "students" in data and "total" in data:
                    filter_desc = f"search='{search}'" if search else ""
                    filter_desc += f" status='{status}'" if status else ""
                    return self.log_test("Get Students List", True, f"- Found: {data['total']} students {filter_desc}"), data
                else:
                    return self.log_test("Get Students List", False, "- Invalid response structure"), None
            else:
                return self.log_test("Get Students List", False, f"- Status: {response.status_code}"), None
                
        except Exception as e:
            return self.log_test("Get Students List", False, f"- Error: {str(e)}"), None

    def test_get_student_by_id(self, student_id):
        """Test getting a specific student by ID"""
        try:
            response = self.session.get(f"{self.base_url}/api/students/{student_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == student_id:
                    return self.log_test("Get Student by ID", True, f"- Name: {data.get('name')}")
                else:
                    return self.log_test("Get Student by ID", False, "- ID mismatch")
            else:
                return self.log_test("Get Student by ID", False, f"- Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Get Student by ID", False, f"- Error: {str(e)}")

    def test_update_student(self, student_id, update_data):
        """Test updating a student"""
        try:
            response = self.session.put(
                f"{self.base_url}/api/students/{student_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == student_id:
                    return self.log_test("Update Student", True, f"- Updated: {update_data}")
                else:
                    return self.log_test("Update Student", False, "- ID mismatch")
            else:
                return self.log_test("Update Student", False, f"- Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Update Student", False, f"- Error: {str(e)}")

    def test_delete_student(self, student_id):
        """Test deleting a student"""
        try:
            response = self.session.delete(f"{self.base_url}/api/students/{student_id}", timeout=10)
            
            if response.status_code == 200:
                return self.log_test("Delete Student", True, f"- Deleted ID: {student_id}")
            else:
                return self.log_test("Delete Student", False, f"- Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Delete Student", False, f"- Error: {str(e)}")

    def test_email_uniqueness(self):
        """Test email uniqueness validation"""
        print("\n📧 Testing Email Uniqueness...")
        
        # Create first student
        student1 = {
            "name": "Test Student 1",
            "email": "unique.test@example.com",
            "course": "Computer Science",
            "status": "active"
        }
        
        success1, student_id1 = self.test_create_student(student1)
        if not success1:
            return False
            
        # Try to create second student with same email
        student2 = {
            "name": "Test Student 2", 
            "email": "unique.test@example.com",  # Same email
            "course": "Mathematics",
            "status": "active"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/students",
                json=student2,
                timeout=10
            )
            
            if response.status_code == 400:
                success = self.log_test("Email Uniqueness Validation", True, "- Correctly rejected duplicate email")
            else:
                success = self.log_test("Email Uniqueness Validation", False, f"- Expected 400, got {response.status_code}")
                
        except Exception as e:
            success = self.log_test("Email Uniqueness Validation", False, f"- Error: {str(e)}")
        
        # Clean up
        if student_id1:
            self.test_delete_student(student_id1)
            
        return success

    def test_search_functionality(self):
        """Test search functionality"""
        print("\n🔍 Testing Search Functionality...")
        
        # Create test students
        test_students = [
            {"name": "Alice Johnson", "email": "alice.j@test.com", "course": "Computer Science", "status": "active"},
            {"name": "Bob Smith", "email": "bob.s@test.com", "course": "Mathematics", "status": "inactive"},
            {"name": "Charlie Brown", "email": "charlie.b@test.com", "course": "Physics", "status": "active"}
        ]
        
        created_ids = []
        for student in test_students:
            success, student_id = self.test_create_student(student)
            if success and student_id:
                created_ids.append(student_id)
        
        time.sleep(1)  # Allow for data consistency
        
        # Test search by name
        success, data = self.test_get_students(search="Alice")
        if success and data and len(data["students"]) > 0:
            self.log_test("Search by Name", True, f"- Found {len(data['students'])} results")
        else:
            self.log_test("Search by Name", False, "- No results found")
            
        # Test search by course
        success, data = self.test_get_students(search="Computer")
        if success and data:
            self.log_test("Search by Course", True, f"- Found {len(data['students'])} results")
        else:
            self.log_test("Search by Course", False, "- No results found")
        
        # Clean up
        for student_id in created_ids:
            self.test_delete_student(student_id)

    def test_status_filter(self):
        """Test status filtering"""
        print("\n🏷️ Testing Status Filter...")
        
        # Test filter by active status
        success, data = self.test_get_students(status="active")
        if success and data is not None:
            self.log_test("Filter by Active Status", True, f"- Found {data['total']} active students")
        else:
            self.log_test("Filter by Active Status", False, "- Failed to filter")
            
        # Test filter by inactive status  
        success, data = self.test_get_students(status="inactive")
        if success and data is not None:
            self.log_test("Filter by Inactive Status", True, f"- Found {data['total']} inactive students")
        else:
            self.log_test("Filter by Inactive Status", False, "- Failed to filter")

    def test_pagination(self):
        """Test pagination functionality"""
        print("\n📄 Testing Pagination...")
        
        # Test first page
        success, data = self.test_get_students(page=1, limit=5)
        if success and data:
            self.log_test("Pagination - Page 1", True, f"- Page: {data.get('page')}, Limit: {data.get('limit')}")
        else:
            self.log_test("Pagination - Page 1", False, "- Failed to get page 1")

    def test_logout(self):
        """Test logout functionality"""
        try:
            response = self.session.post(f"{self.base_url}/api/auth/logout", timeout=10)
            
            if response.status_code == 200:
                return self.log_test("Logout", True, "- Successfully logged out")
            else:
                return self.log_test("Logout", False, f"- Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Logout", False, f"- Error: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Student Management System Backend API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test authentication first
        if not self.test_auth_login():
            print("\n❌ Authentication failed - stopping tests")
            return False
            
        self.test_auth_me()
        
        print("\n👥 Testing Student CRUD Operations...")
        
        # Test basic CRUD operations
        test_student = {
            "name": "John Doe",
            "email": "john.doe@test.com", 
            "course": "Computer Science",
            "status": "active"
        }
        
        # Create student
        success, student_id = self.test_create_student(test_student)
        if not success or not student_id:
            print("❌ Failed to create student - skipping dependent tests")
        else:
            # Test get by ID
            self.test_get_student_by_id(student_id)
            
            # Test update
            update_data = {"course": "Data Science", "status": "inactive"}
            self.test_update_student(student_id, update_data)
            
            # Test delete
            self.test_delete_student(student_id)
        
        # Test list students
        self.test_get_students()
        
        # Test advanced features
        self.test_email_uniqueness()
        self.test_search_functionality()
        self.test_status_filter()
        self.test_pagination()
        
        # Test logout
        self.test_logout()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    """Main test execution"""
    tester = StudentManagementAPITester()
    success = tester.run_comprehensive_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())