import requests

BASE_URL = "http://127.0.0.1:8000"

def login(email, password):
    url = f"{BASE_URL}/api/v1/auth/login"
    data = {"email": email, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Login failed:", response.text)
    return None

def test_endpoints():
    print("Fetching OpenAPI schema...")
    try:
        schema = requests.get(f"{BASE_URL}/openapi.json").json()
    except Exception as e:
        print("Failed to get OpenAPI schema:", e)
        return

    admin_token = login("admin@ems.edu.vn", "Admin@123")
    print(f"Admin Token obtained: {admin_token is not None}")
    
    teacher_token = login("teacher1@ems.edu.vn", "Admin@123")
    print(f"Teacher Token obtained: {teacher_token is not None}")

    student_token = login("student1@ems.edu.vn", "Admin@123")
    print(f"Student Token obtained: {student_token is not None}")

    if not admin_token:
        print("Could not get admin token, cannot proceed.")
        return

    headers = {"Authorization": f"Bearer {admin_token}"}

    paths = schema.get("paths", {})
    failed_endpoints = []

    for path, methods in paths.items():
        if 'get' in methods:
            # We only test GET requests safely
            # Replace path parameters with dummy values
            test_path = path
            if "{user_id}" in test_path: test_path = test_path.replace("{user_id}", "U001")
            if "{teacher_id}" in test_path: test_path = test_path.replace("{teacher_id}", "T001")
            if "{course_id}" in test_path: test_path = test_path.replace("{course_id}", "CS101")
            if "{class_id}" in test_path: test_path = test_path.replace("{class_id}", "C001")
            if "{assignment_id}" in test_path: test_path = test_path.replace("{assignment_id}", "1")
            if "{doc_id}" in test_path: test_path = test_path.replace("{doc_id}", "1")

            url = f"{BASE_URL}{test_path}"
            print(f"Testing GET {url}...")
            res = requests.get(url, headers=headers)
            print(f"  -> {res.status_code}")
            
            if res.status_code >= 500:
                print(f"  *** BUG FOUND in GET {path}: {res.text}")
                failed_endpoints.append((path, res.status_code, res.text))

    print("\n--- TEST SUMMARY ---")
    if failed_endpoints:
        print(f"Found {len(failed_endpoints)} endpoints with 500 errors:")
        for ep, code, txt in failed_endpoints:
            print(f" - {ep}: {code} - {txt[:100]}")
    else:
        print("No 500 errors found in GET requests.")

if __name__ == "__main__":
    test_endpoints()
