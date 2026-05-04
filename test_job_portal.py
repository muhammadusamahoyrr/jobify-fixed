import unittest
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ─────────────────────────────────────────────────────────────────
#  CONFIG  ← update emails/passwords to match your real accounts
# ─────────────────────────────────────────────────────────────────
BASE_URL          = "http://3.212.77.197"       # Nginx → React frontend
API_URL           = "http://3.212.77.197:8080"  # Node backend (port 8080)

EMPLOYER_EMAIL    = "employer@jobportal.com"
EMPLOYER_PASSWORD = "Employer@123"

SEEKER_EMAIL      = "seeker@jobportal.com"
SEEKER_PASSWORD   = "Seeker@123"

# ─────────────────────────────────────────────────────────────────
#  HELPER — log in via API and return the JWT token
# ─────────────────────────────────────────────────────────────────
def get_token(email, password):
    """
    POST /auth/signin and return the JWT string, or None if login fails.
    Works with whatever key the server uses: token / accessToken / jwt.
    """
    try:
        r = requests.post(
            f"{API_URL}/auth/signin",
            json={"email": email, "password": password},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return (
                data.get("token")
                or data.get("accessToken")
                or data.get("jwt")
            )
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────
#  DRIVER FACTORY — headless Chrome (runs on EC2 / Jenkins / Docker)
# ─────────────────────────────────────────────────────────────────
def get_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)


# ═════════════════════════════════════════════════════════════════
#  CLASS 1 — DevOps Smoke Tests  (server + frontend health checks)
# ═════════════════════════════════════════════════════════════════
class Test01_DevOpsSmoke(unittest.TestCase):

    def test_01_frontend_returns_200(self):
        """GET / must return 200 and Content-Type: text/html."""
        r = requests.get(BASE_URL, timeout=10)
        self.assertEqual(r.status_code, 200,
                         f"Frontend returned {r.status_code}")
        self.assertIn("text/html", r.headers.get("Content-Type", ""),
                      "Response is not HTML")

    def test_02_backend_server_reachable(self):
        """
        Any HTTP response from the backend proves the Node process is running.
        A ConnectionError means it is down.
        """
        try:
            r = requests.get(f"{API_URL}/", timeout=10)
            self.assertIsNotNone(r.status_code)
        except requests.exceptions.ConnectionError:
            self.fail(f"Backend is NOT reachable at {API_URL}")

    def test_03_auth_route_exists(self):
        """POST /auth/signin must not return 404 (route is mounted)."""
        r = requests.post(
            f"{API_URL}/auth/signin",
            json={"email": "x@x.com", "password": "x"},
            timeout=10
        )
        self.assertNotEqual(r.status_code, 404,
                            "/auth/signin returned 404 — route not mounted")

    def test_04_employer_route_exists(self):
        """GET /employer/jobs must not return 404 (route is mounted)."""
        r = requests.get(f"{API_URL}/employer/jobs", timeout=10)
        self.assertNotEqual(r.status_code, 404,
                            "/employer/jobs returned 404 — route not mounted")

    def test_05_jobseeker_route_exists(self):
        """GET /jobseeker/cv must not return 404 (route is mounted)."""
        r = requests.get(f"{API_URL}/jobseeker/cv", timeout=10)
        self.assertNotEqual(r.status_code, 404,
                            "/jobseeker/cv returned 404 — route not mounted")


# ═════════════════════════════════════════════════════════════════
#  CLASS 2 — Authentication API Tests
# ═════════════════════════════════════════════════════════════════
class Test02_AuthAPI(unittest.TestCase):

    def test_06_signup_empty_body_rejected(self):
        """POST /auth/signup with no body → 400 or 422."""
        r = requests.post(f"{API_URL}/auth/signup", json={}, timeout=10)
        self.assertIn(r.status_code, [400, 422],
                      f"Empty signup should be rejected, got {r.status_code}")

    def test_07_signin_wrong_password_rejected(self):
        """POST /auth/signin with wrong password → 400 or 401."""
        r = requests.post(
            f"{API_URL}/auth/signin",
            json={"email": EMPLOYER_EMAIL, "password": "WRONGPASS999"},
            timeout=10
        )
        self.assertIn(r.status_code, [400, 401],
                      f"Wrong password should be rejected, got {r.status_code}")

    def test_08_signin_unknown_email_rejected(self):
        """POST /auth/signin with non-existent email → 400, 401, or 404."""
        r = requests.post(
            f"{API_URL}/auth/signin",
            json={"email": "ghost_xyz_000@nowhere.com", "password": "any"},
            timeout=10
        )
        self.assertIn(r.status_code, [400, 401, 404],
                      f"Unknown email should be rejected, got {r.status_code}")

    def test_09_employer_signin_returns_token(self):
        """Valid employer login → 200 + JWT token in response body."""
        r = requests.post(
            f"{API_URL}/auth/signin",
            json={"email": EMPLOYER_EMAIL, "password": EMPLOYER_PASSWORD},
            timeout=10
        )
        if r.status_code != 200:
            self.skipTest(
                f"Employer account not found (status {r.status_code}). "
                "Create the account first, then re-run."
            )
        data = r.json()
        token = data.get("token") or data.get("accessToken") or data.get("jwt")
        self.assertIsNotNone(token, f"No token in response: {data}")

    def test_10_jobseeker_signin_returns_token(self):
        """Valid jobseeker login → 200 + JWT token in response body."""
        r = requests.post(
            f"{API_URL}/auth/signin",
            json={"email": SEEKER_EMAIL, "password": SEEKER_PASSWORD},
            timeout=10
        )
        if r.status_code != 200:
            self.skipTest(
                f"Jobseeker account not found (status {r.status_code}). "
                "Create the account first, then re-run."
            )
        data = r.json()
        token = data.get("token") or data.get("accessToken") or data.get("jwt")
        self.assertIsNotNone(token, f"No token in response: {data}")


# ═════════════════════════════════════════════════════════════════
#  CLASS 3 — Authorization Tests  (protected routes)
# ═════════════════════════════════════════════════════════════════
class Test03_AuthorizationAPI(unittest.TestCase):
    """
    Every /employer and /jobseeker route uses authenticateToken middleware.
    Requests without a token or with a fake token must be rejected.
    """

    def test_11_employer_jobs_no_token_blocked(self):
        """GET /employer/jobs without Authorization header → 401 or 403."""
        r = requests.get(f"{API_URL}/employer/jobs", timeout=10)
        self.assertIn(r.status_code, [401, 403],
                      f"No-token request should be blocked, got {r.status_code}")

    def test_12_jobseeker_cv_no_token_blocked(self):
        """GET /jobseeker/cv without Authorization header → 401 or 403."""
        r = requests.get(f"{API_URL}/jobseeker/cv", timeout=10)
        self.assertIn(r.status_code, [401, 403],
                      f"No-token request should be blocked, got {r.status_code}")

    def test_13_fake_token_rejected(self):
        """GET /employer/jobs with a fake Bearer token → 401 or 403."""
        headers = {"Authorization": "Bearer this.is.a.fake.token"}
        r = requests.get(f"{API_URL}/employer/jobs",
                         headers=headers, timeout=10)
        self.assertIn(r.status_code, [401, 403],
                      f"Fake token should be rejected, got {r.status_code}")

    def test_14_post_job_no_token_blocked(self):
        """POST /employer/jobs without token → 401 or 403."""
        payload = {"title": "Hacker Job", "description": "test", "location": "Remote"}
        r = requests.post(f"{API_URL}/employer/jobs",
                          json=payload, timeout=10)
        self.assertIn(r.status_code, [401, 403],
                      f"Unauthenticated job post should be blocked, got {r.status_code}")

    def test_15_apply_no_token_blocked(self):
        """POST /jobseeker/apply without token → 401, 403, or 404."""
        r = requests.post(f"{API_URL}/jobseeker/apply",
                          json={"jobId": "fakeid123"}, timeout=10)
        self.assertIn(r.status_code, [401, 403, 404],
                      f"Unauthenticated apply should be blocked, got {r.status_code}")


# ═════════════════════════════════════════════════════════════════
#  CLASS 4 — Employer API Tests  (with valid token)
# ═════════════════════════════════════════════════════════════════
class Test04_EmployerAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Log in once before all employer tests and store the token."""
        cls.token = get_token(EMPLOYER_EMAIL, EMPLOYER_PASSWORD)
        cls.headers = {"Authorization": f"Bearer {cls.token}"} if cls.token else {}

    def _skip_if_no_token(self):
        if not self.token:
            self.skipTest(
                "Employer token unavailable — create the employer account first."
            )

    def test_16_employer_can_fetch_own_jobs(self):
        """GET /employer/jobs with valid token → 200."""
        self._skip_if_no_token()
        r = requests.get(f"{API_URL}/employer/jobs",
                         headers=self.headers, timeout=10)
        self.assertEqual(r.status_code, 200,
                         f"Expected 200, got {r.status_code}: {r.text}")

    def test_17_employer_post_job_valid_data(self):
        """POST /employer/jobs with all required fields → 200 or 201."""
        self._skip_if_no_token()
        payload = {
            "title":       "Software Engineer Intern",
            "description": "Work on exciting MERN projects",
            "location":    "Lahore, Pakistan",
            "salary":      "50000",
            "type":        "Full-time"
        }
        r = requests.post(f"{API_URL}/employer/jobs",
                          json=payload, headers=self.headers, timeout=10)
        self.assertIn(r.status_code, [200, 201],
                      f"Valid job post failed: {r.status_code} — {r.text}")

    def test_18_employer_post_job_missing_title_rejected(self):
        """POST /employer/jobs without 'title' field → 400 or 422."""
        self._skip_if_no_token()
        payload = {"description": "No title here", "location": "Remote"}
        r = requests.post(f"{API_URL}/employer/jobs",
                          json=payload, headers=self.headers, timeout=10)
        self.assertIn(r.status_code, [400, 422],
                      f"Missing-title job should be rejected, got {r.status_code}")


# ═════════════════════════════════════════════════════════════════
#  CLASS 5 — UI Tests  (Selenium headless Chrome)
# ═════════════════════════════════════════════════════════════════
class Test05_UIFlow(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()
        self.wait   = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def test_19_react_app_mounts(self):
        """Page source must contain HTML — not a blank page or Node error."""
        self.driver.get(BASE_URL)
        time.sleep(3)
        src = self.driver.page_source
        self.assertNotIn("Cannot GET", src,
                         "Got a raw Node error instead of the React app")
        self.assertGreater(len(src), 500,
                           "Page source too short — React may not have mounted")

    def test_20_login_page_has_inputs(self):
        """/login must render at least two inputs (email + password)."""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        self.assertGreaterEqual(len(inputs), 2,
                                "Expected at least 2 inputs on /login")

    def test_21_wrong_password_shows_error_in_ui(self):
        """Wrong credentials must show an error — not redirect to dashboard."""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) < 2:
            self.skipTest("Login inputs not found")

        inputs[0].clear()
        inputs[0].send_keys(EMPLOYER_EMAIL)
        inputs[1].clear()
        inputs[1].send_keys("DEFINITELYWRONGPASSWORD")
        self.driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(3)

        page = self.driver.page_source.lower()
        error_visible = any(w in page for w in
                            ["invalid", "incorrect", "wrong", "error",
                             "failed", "unauthorized", "not found"])
        self.assertTrue(error_visible,
                        "No error message shown for wrong password in the UI")

    def test_22_employer_login_reaches_dashboard(self):
        """Employer login must redirect to an employer-specific view."""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) < 2:
            self.skipTest("Login inputs not found")

        inputs[0].clear()
        inputs[0].send_keys(EMPLOYER_EMAIL)
        inputs[1].clear()
        inputs[1].send_keys(EMPLOYER_PASSWORD)
        self.driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(4)

        combined = self.driver.current_url.lower() + self.driver.page_source.lower()
        self.assertTrue(
            any(w in combined for w in
                ["dashboard", "employer", "post job", "my jobs", "post a job"]),
            f"Employer login did not reach employer view. URL: {self.driver.current_url}"
        )

    def test_23_jobseeker_login_reaches_dashboard(self):
        """Jobseeker login must redirect to a jobseeker-specific view."""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) < 2:
            self.skipTest("Login inputs not found")

        inputs[0].clear()
        inputs[0].send_keys(SEEKER_EMAIL)
        inputs[1].clear()
        inputs[1].send_keys(SEEKER_PASSWORD)
        self.driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(4)

        combined = self.driver.current_url.lower() + self.driver.page_source.lower()
        self.assertTrue(
            any(w in combined for w in
                ["dashboard", "jobseeker", "seeker", "browse", "apply", "jobs"]),
            f"Jobseeker login did not reach seeker view. URL: {self.driver.current_url}"
        )

    def test_24_signup_page_has_form(self):
        """/signup or /register must render a form with input fields."""
        for path in ["/signup", "/register"]:
            self.driver.get(f"{BASE_URL}{path}")
            time.sleep(2)
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            if len(inputs) >= 2:
                return
        self.fail("Could not find a signup/register page with inputs")

    def test_25_logout_returns_to_login_or_home(self):
        """After logout the user must land on the login page or home URL."""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) < 2:
            self.skipTest("Login inputs not found")

        inputs[0].send_keys(EMPLOYER_EMAIL)
        inputs[1].send_keys(EMPLOYER_PASSWORD)
        self.driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(4)

        page = self.driver.page_source.lower()
        if "logout" not in page and "sign out" not in page:
            self.skipTest("Logout button not visible — employer account may not exist yet")

        try:
            logout = self.driver.find_element(
                By.XPATH,
                "//*["
                "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'logout')"
                " or contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sign out')"
                "]"
            )
            logout.click()
            time.sleep(3)
        except Exception:
            self.skipTest("Could not locate/click the logout button")

        after = self.driver.current_url.lower()
        self.assertTrue(
            "login" in after or "home" in after
            or after.rstrip("/") == BASE_URL.lower(),
            f"After logout, landed on unexpected URL: {self.driver.current_url}"
        )


# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    unittest.main(verbosity=2)
