import time

from . import WebDriverWait
from sebrowser import SeleniumBrowser
from runtime import load_strategies

# Symbolic Type Classes
class Label:
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return f"<ElementLabel name={self._name}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name


class Matcher:
    def __init__(self, by, value):
        self._by = by
        self._value = value
        self._matches = []

    def __len__(self):
        return len(self._matches)

    def __repr__(self):
        return f"<ElementMatcher by={self._by} value={self._value}>"

    def __str__(self):
        return f"Matcher(by={self._by}, value={self._value}, matches={len(self)})"

    @property
    def matches(self):
        return self._matches

    @matches.setter
    def matches(self, matches):
        if isinstance(matches, list):
            self._matches = matches
        else:
            raise ValueError("Matches must be a list")


class Element:
    def __init__(self, element, label=None, match=None):
        self.element = element
        self._label = Label(label) if label else None
        self._match = Matcher(*match) if match else None

    def __repr__(self):
        return f"<SymbolicElement label={self._label}>"

    def label(self, label):
        self._label = Label(label)
        return self

    def match(self, idx):
        if self._match and 0 <= idx < len(self._match):
            return self._match.matches[idx]
        raise ValueError("No matcher or index out of range")

    @property
    def matches(self):
        return self._match.matches if self._match else []

    @property
    def match_count(self):
        return len(self._match) if self._match else 0

    def __len__(self):
        return self.match_count


# Python Selenium Browser Kit Abstraction Class
class PySBK(SeleniumBrowser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log.debug("Initializing PySBK")

        strategies = load_strategies()
        self.find_strategies = strategies.get("find_strategies", {})
        self.click_behaviors = strategies.get("click_behaviors", {})
        self.type_modes = strategies.get("type_modes", {})
        self.expect_conditions = strategies.get("expect_conditions", {})
        self.go_behaviors = strategies.get("go_behaviors", {})

        self.registry = {}

    # Symbolic resolution
    def resolve(self, target=None, which="only", by=None, match=None):
        if isinstance(target, Element):
            return target.element

        if isinstance(target, Label):
            el = self.registry.get(target.name)
            return el.element if el else None

        if isinstance(target, Matcher):
            elements = self.driver.find_elements(target._by, target._value)
            target.matches = elements
            return elements[0] if which == "only" else elements[which]

        if by and match:
            return self.find(by, match, which).element

        return None

    # Registry access
    def register(self, label, element):
        self.registry[label] = element
        return element

    def get_label(self, name):
        return self.registry.get(name)

    # Element resolution
    def find(self, by, match, which="only", label=None):
        elements = self.driver.find_elements(by, match)
        if not elements:
            self.last_error = Exception("No elements found")
            return None

        matcher = Matcher(by, match)
        matcher.matches = elements

        el = elements[0] if which == "only" else (
            elements[which] if isinstance(which, int) else self.find_strategies.get(which, lambda x: x[0])(elements)
        )

        symbolic = Element(el, label=label, match=(by, match))
        if label:
            self.register(label, symbolic)
        return symbolic

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
    def alertPresent(self): return self.expect(None, None, "alert")
    def console(self, namespace="_PySBK"): return self.get_console_logs(namespace)
    def frameReady(self, **kwargs): return self.expect(kwargs.get("by"), kwargs.get("match"), "frame")
    def hasValue(self, value, **kwargs): return self.expect(kwargs.get("by"), kwargs.get("match"), "value", value=value)
    def inject(self, jscode): self.inject_script(jscode)
    def isClickable(self, **kwargs): return self.expect(kwargs.get("by"), kwargs.get("match"), "clickable")
    def isPresent(self, **kwargs): return self.expect(kwargs.get("by"), kwargs.get("match"), "present")
    def isSelected(self, **kwargs): return self.expect(kwargs.get("by"), kwargs.get("match"), "selected")
    def isStale(self, element): return self.expect(None, element, "stale")
    def isText(self, text, mode="partial", **kwargs): return self.expect(kwargs.get("by"), kwargs.get("match"), "text", value=text, mode=mode)
    def isVisible(self, **kwargs): return self.expect(kwargs.get("by"), kwargs.get("match"), "visible")
    def track(self): self.inject_tracker()

    # Action methods
    def click(self, target=None, behavior="default", **kwargs):
        el = self.resolve(target=target, **kwargs)
        if el and behavior in self.click_behaviors:
            self.click_behaviors[behavior](el)
        return Element(el) if el else None

    def get_text(self, target=None, **kwargs):
        el = self.resolve(target=target, **kwargs)
        return el.text.strip() if el else None

    def get_attribute(self, attr, target=None, **kwargs):
        el = self.resolve(target=target, **kwargs)
        return el.get_attribute(attr) if el else None

    def go(self, url, reinject=True, track_redirects=True, behavior="default"):
        if behavior in self.go_behaviors:
            self.go_behaviors[behavior](self.driver, url)

        if track_redirects:
            time.sleep(1)
            final_url = self.driver.current_url
            if final_url != url:
                self.last_redirect = final_url

        if reinject:
            self.track()
            self.inject_dom_agent()

    def type(self, text, target=None, mode="default", term="", **kwargs):
        el = self.resolve(target=target, **kwargs)
        if el and mode in self.type_modes:
            self.type_modes[mode](el, text) if mode != "type_then_term" else self.type_modes[mode](el, text, term)
        return Element(el) if el else None
