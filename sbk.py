import random, re

from sebrowser import SeleniumBrowser

class PySBK(SeleniumBrowser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log.debug("Initializing PySBK")

    def find(self, by, match, which="all"):
        try:
            if by in [By.ID, By.Name]:
                return self.driver.find_element(by, match)
            else:
                elements = self.driver.find_elements(by, match)
                if not elements:
                    raise Exception("No elements found")
                if isinstance(which, int):
                    return elements[which]
                if isinstance(which, str):
                    WHICH = {
                        "all": lambda els: els,
                        "first": lambda els: els[0],
                        "second": lambda els: els[1] if len(els) > 1 else None,
                        "middle": lambda els: els[round(len(els)/2)] if els else None,
                        "last": lambda els: els[-1],
                        "random": lambda els: random.choice(els) if els else None,
                    }
                    key = which.lower()
                    if key in WHICH:
                        return WHICH[key](elements)
                    else:
                        raise ValueError(f"Invalid 'which': {which}")
                else:
                    return elements
        except Exception as e:
            self.last_error = e
            return None

    def expect(self, by, match, condition="present", value=False, mode="partial"):
        try:
            if condition == "present":
                return EC.presence_of_element_located((by, match))
            elif condition == "visible":
                return EC.visibility_of_element_located((by, match))
            elif condition == "clickable":
                return EC.element_to_be_clickable((by, match))
            elif condition == "text":
                def check(driver):
                    el = driver.find_element(by, match)
                    text = el.text or el.get_attribute("value") or ""
                    if mode == "exact":
                        return text == value
                    elif mode == "partial":
                        return value in text
                    elif mode == "lower":
                        return value.lower() in text.lower()
                    elif mode == "regex":
                        import re
                        return re.search(value, text) is not None
                    return False
                return check
            elif condition == "value":
                return EC.text_to_be_present_in_element_value((by, match), value)
            elif condition == "selected":
                return EC.element_to_be_selected((by, match))
            elif condition == "stale":
                return EC.staleness_of(match)
            elif condition == "alert":
                return EC.alert_is_present()
            elif condition == "frame":
                return EC.frame_to_be_available_and_switch_to_it((by, match))
            else:
                raise Exception(f"Unknown condition: {condition}")
        except Exception as e:
            self.last_error = e
            return None

    def wait(self, condition, timeout=None):
        try:
            return WebDriverWait(self.driver, timeout or self.timeout).until(condition)
        except Exception as e:
            self.last_error = e
            return None

    # Stub methods
    def isPresent(self, by, match): 
        return self.expect(by, match, "present")
    def isVisible(self, by, match): 
        return self.expect(by, match, "visible")
    def isClickable(self, by, match): 
        return self.expect(by, match, "clickable")
    def isText(self, by, match, text, mode="partial"): 
        return self.expect(by, match, "text", value=text, mode=mode)
    def hasValue(self, by, match, value): 
        return self.expect(by, match, "value", value=value)
    def isSelected(self, by, match): 
        return self.expect(by, match, "selected")
    def isStale(self, element): 
        return self.expect(None, element, "stale")
    def alertPresent(self): 
        return self.expect(None, None, "alert")
    def frameReady(self, by, match): 
        return self.expect(by, match, "frame")

    # Action methods
    def click(self, by, match, which="only"):
        el = self.find(by, match, which)
        if el: el.click()

    def get_text(self, by, match, which="only"):
        el = self.find(by, match, which)
        return el.text.strip() if el else None

    def get_attribute(self, by, match, attr, which="only"):
        el = self.find(by, match, which)
        return el.get_attribute(attr) if el else None

    def type(self, by, match, text, term="", clear=True, which="only"):
        el = self.find(by, match, which)
        if el:
            if clear: el.clear()
            el.send_keys(text+term)

    def go(self, url, reinject=True, track_redirects=True, timeout=10):
        self.driver.get(url)
        if track_redirects:
            time.sleep(1)
            final_url = self.driver.current_url
            if final_url != url:
                self.last_redirect = final_url
        if reinject:
            self.inject_tracker()
            self.inject_dom_agent()

