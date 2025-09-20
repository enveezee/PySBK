## WIP, until the 1.0 release coming very soon now, this readme and its examples especially are subject to change and inaccuracy.

# PySBK

**PySBK** is a symbolic browser automation runtime built on top of Selenium, designed for cognitive clarity, modular extensibility, and survival-grade control. It abstracts away procedural mess and exposes a declarative interface for building resilient, intention-driven agents.

---

## 🧠 Philosophy

PySBK isn't just a wrapper — it's a framework for reclaiming authorship in hostile ecosystems. It externalizes behavior into symbolic schemas, allowing users and developers to customize browser logic without touching the core codebase.

- **Declarative**: All behaviors are schema-driven and inspectable.
- **Extensible**: Drop-in strategies for `find`, `click`, `type`, `expect`, and more.
- **Resilient**: Survives DOM mutations, platform revocation, and brittle APIs.
- **Modular**: Clean separation between runtime logic and symbolic dispatch.

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
```

Example Usage:
```python
from PySBK.sbk import PySBK

bot = PySBK()
bot.go("https://example.com")
bot.click(By.CSS_SELECTOR, ".submit-button", which="first")
bot.type(By.NAME, "email", "user@example.com", mode="type_then_tab")
```
