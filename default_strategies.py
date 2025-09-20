import re, random

default_strategies = {
    "find_strategies": {
        "all": lambda els: els,
        "first": lambda els: els[0],
        "second": lambda els: els[1] if len(els) > 1 else None,
        "middle": lambda els: els[round(len(els)/2)] if els else None,
        "last": lambda els: els[-1],
        "random": lambda els: random.choice(els) if els else None,
    },

    "click_behaviors": {
        "default": lambda el: el.click(),
        "safe": lambda el: el.click() if el.is_displayed() and el.is_enabled() else None,
        "double": lambda el: [el.click(), el.click()],
    },

    "type_modes": {
        "default": lambda el, text: el.send_keys(text),
        "clear_then_type": lambda el, text: (el.clear(), el.send_keys(text)),
        "type_then_enter": lambda el, text: el.send_keys(text + Keys.ENTER),
        "type_then_tab": lambda el, text: el.send_keys(text + Keys.TAB),
        "type_then_term": lambda el, text, term="": el.send_keys(text + term),
    },

    "expect_conditions": {
        "present": lambda by, match: EC.presence_of_element_located((by, match)),
        "visible": lambda by, match: EC.visibility_of_element_located((by, match)),
        "clickable": lambda by, match: EC.element_to_be_clickable((by, match)),
        "selected": lambda by, match: EC.element_to_be_selected((by, match)),
        "value": lambda by, match, value: EC.text_to_be_present_in_element_value((by, match), value),
        "text_exact": lambda driver, by, match, value: driver.find_element(by, match).text == value,
        "text_partial": lambda driver, by, match, value: value in driver.find_element(by, match).text,
        "text_lower": lambda driver, by, match, value: value.lower() in driver.find_element(by, match).text.lower(),
        "text_regex": lambda driver, by, match, value: re.search(value, driver.find_element(by, match).text or "") is not None,
        "stale": lambda el: EC.staleness_of(el),
        "alert": lambda: EC.alert_is_present(),
        "frame": lambda by, match: EC.frame_to_be_available_and_switch_to_it((by, match)),
    },

    "go_behaviors": {
        "default": lambda driver, url: driver.get(url),
        "track_redirect": lambda driver, url: (driver.get(url), time.sleep(1), driver.current_url),
        "reinject": lambda agent: (agent.inject_tracker(), agent.inject_dom_agent()),
    }
}
