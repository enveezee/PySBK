import shutil, subprocess

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys    
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
except Exception as e:
    print(f'[SeleniumBrowser] Import error: {e}')

import runtime

class SeleniumBrowser:
    def __init__(self, **kwargs):
        self.log = runtime.setup_logger()
        self.log.info("Initializing SeleniumBrowser")
        config = load_config()
        PARAMS = {
            "browser": "chromium",
            "clone": "true",
            "headless": "false",
            "profile": None,
            "URL": None,
        }
        for key, default in PARAMS.items():
            raw_value = kwargs.get(key, config.get(key, default))
            if isinstance(default, str) and default in ("true", "false"):
                resolved = raw_value == "true"
            else:
                resolved = raw_value
        self.browsers = {}  # registry of all detected browsers
        self.detect_browsers()

    def detect_browsers(self):
        candidates = {
            "brave": ["brave-browser", "brave"],
            "chrome": ["google-chrome", "chrome"],
            "chromium": ["chromium-browser", "chromium"],
            "edge": ["microsoft-edge", "edge"],
            "firefox": ["firefox", "firefox-esr"]
        }

        for name, binaries in candidates.items():
            for binary in binaries:
                path = shutil.which(binary)
                if path:
                    version = self.get_browser_version(path)
                    profile_path, user_data_dir = runtime.resolve_profile(name)
                    options = self.build_options(name, path, profile_path, user_data_dir)
                    service = self.build_service(name)
                    self.browsers[name] = {
                        "name": name,
                        "binary": path,
                        "version": version,
                        "profile_path": profile_path,
                        "user_data_dir": user_data_dir,
                        "options": options,
                        "service": service,
                        "driver": None,
                        "process": None,
                        "status": "idle"
                    }
                    break  # stop after first valid binary

    def get_browser_version(self, binary):
        try:
            result = subprocess.run([binary, "--version"], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def build_options(self, name, binary, profile_path, user_data_dir):
        if name in ["brave", "chrome", "chromium"]:
            options = webdriver.ChromeOptions()
            options.binary_location = binary
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument(f"--profile-directory={profile_path}")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            return options

        elif name == "edge":
            options = webdriver.EdgeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument(f"--profile-directory={profile_path}")
            return options

        elif name == "firefox":
            options = webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            return options

        return None

    def build_service(self, name):
        try:
            if name in ["brave", "chrome", "chromium"]:
                return webdriver.Chrome.service.Service(ChromeDriverManager().install())
            elif name == "edge":
                return webdriver.Edge.service.Service(EdgeChromiumDriverManager().install())
            elif name == "firefox":
                return webdriver.Firefox.service.Service(GeckoDriverManager().install())
        except Exception as e:
            print(f"[SeleniumBrowser] Failed to build service for {name}: {e}")
            return None

    def launch_browser(self, name, mode="selenium"):
        if name not in self.browsers:
            print(f"[SeleniumBrowser] Browser '{name}' not available.")
            return

        browser = self.browsers[name]

        # Stop any existing session
        if browser["status"] == "selenium" and browser["driver"]:
            browser["driver"].quit()
        elif browser["status"] == "subprocess" and browser["process"]:
            browser["process"].terminate()

        try:
            if mode == "selenium":
                driver_class = getattr(webdriver, name.capitalize()) if name != "chromium" else webdriver.Chrome
                browser["driver"] = driver_class(service=browser["service"], options=browser["options"])
                browser["status"] = "selenium"

            elif mode == "headless":
                browser["options"].add_argument("--headless=new")
                driver_class = getattr(webdriver, name.capitalize()) if name != "chromium" else webdriver.Chrome
                browser["driver"] = driver_class(service=browser["service"], options=browser["options"])
                browser["status"] = "headless"

            elif mode == "subprocess":
                browser["process"] = subprocess.Popen([browser["binary"]])
                browser["status"] = "subprocess"

        except Exception as e:
            print(f"[SeleniumBrowser] Failed to launch {name} in mode '{mode}': {e}")
            browser["status"] = "error"
            self.last_error = e

    def stop_browser(self, name):
        if name not in self.browsers:
            return
        browser = self.browsers[name]
        if browser["status"] == "selenium" and browser["driver"]:
            browser["driver"].quit()
        elif browser["status"] == "subprocess" and browser["process"]:
            browser["process"].terminate()
        browser["status"] = "idle"
        browser["driver"] = None
        browser["process"] = None

    def run_manual_auth(self, name):
        self.stop_browser(name)
        self.launch_browser(name, mode="subprocess")

    def resume_selenium(self, name):
        self.stop_browser(name)
        self.launch_browser(name, mode="selenium")
