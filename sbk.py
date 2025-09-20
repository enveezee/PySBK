import random, re

from sebrowser import SeleniumBrowser
from runtime import load_strategies

class PySBK(SeleniumBrowser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log.debug("Initializing PySBK")

        # Load symbolic strategy registries
        strategies = load_strategies()
        self.find_strategies = strategies.get("find_strategies", {})
        self.click_behaviors = strategies.get("click_behaviors", {})
        self.type_modes = strategies.get("type_modes", {})
        self.expect_conditions = strategies.get("expect_conditions", {})
        self.go_behaviors = strategies.get("go_behaviors", {})

    # Element resolution
    def find(self, by, match, which="all"):
        try:
            if by in {By.ID, By.NAME}:
                return self.driver.find_element(by, match)

            elements = self.driver.find_elements(by, match)
            if not elements:
                raise Exception("No elements found")

            if isinstance(which, int):
                return elements[which]

            if isinstance(which, str):
                key = which.lower()
                if key in self.find_strategies:
                    return self.find_strategies[key](elements)
                raise ValueError(f"Unknown find strategy: {which}")

            return elements
        except Exception as e:
            self.last_error = e
            return None

    # Condition builder
    def expect(self, by, match, condition="present", value=False, mode="partial"):
        try:
            key = f"{condition}_{mode}" if condition == "text" else condition
            resolver = self.expect_conditions.get(key)
            if not resolver:
                raise Exception(f"Unknown condition: {condition}")
            return resolver(self.driver, by, match, value) if "text" in key else resolver(by, match)
        except Exception as e:
            self.last_error = e
            return None

    # Wait wrapper
    def wait(self, condition, timeout=None):
        try:
            return WebDriverWait(self.driver, timeout or self.timeout).until(condition)
        except Exception as e:
            self.last_error = e
            return None

    # Semantic aliases
    def isPresent(self, by, match): return self.expect(by, match, "present")
    def isVisible(self, by, match): return self.expect(by, match, "visible")
    def isClickable(self, by, match): return self.expect(by, match, "clickable")
    def isText(self, by, match, text, mode="partial"): return self.expect(by, match, "text", value=text, mode=mode)
    def hasValue(self, by, match, value): return self.expect(by, match, "value", value=value)
    def isSelected(self, by, match): return self.expect(by, match, "selected")
    def isStale(self, element): return self.expect(None, element, "stale")
    def alertPresent(self): return self.expect(None, None, "alert")
    def frameReady(self, by, match): return self.expect(by, match, "frame")

    # Action methods
    def click(self, by, match, which="only", behavior="default"):
        el = self.find(by, match, which)
        if el and behavior in self.click_behaviors:
            self.click_behaviors[behavior](el)

    def get_text(self, by, match, which="only"):
        el = self.find(by, match, which)
        return el.text.strip() if el else None

    def get_attribute(self, by, match, attr, which="only"):
        el = self.find(by, match, which)
        return el.get_attribute(attr) if el else None

    def type(self, by, match, text, mode="default", which="only", term=""):
        el = self.find(by, match, which)
        if el and mode in self.type_modes:
            self.type_modes[mode](el, text) if mode != "type_then_term" else self.type_modes[mode](el, text, term)

    def go(self, url, reinject=True, track_redirects=True, behavior="default"):
        if behavior in self.go_behaviors:
            self.go_behaviors[behavior](self.driver, url)

        if track_redirects:
            time.sleep(1)
            final_url = self.driver.current_url
            if final_url != url:
                self.last_redirect = final_url

        if reinject:
            self.inject_tracker()
            self.inject_dom_agent()