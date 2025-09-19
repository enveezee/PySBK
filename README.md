Python Selenium Browser Kit

1. Project Overview
PySBK (Python Selenium Browser Kit) is a symbolic SDK that abstracts away Selenium’s brittle boilerplate and exposes a clean, declarative interface for building robust browser-native apps. It’s not a wrapper—it’s a cognitive runtime.

2. Why PySBK Exists
Selenium is powerful, but verbose, inconsistent, and fragile. PySBK ritualizes the setup, profile management, and driver resolution so you never touch raw Selenium again unless you want to. It’s built to Just Work™ across browsers, platforms, and environments.

No more manual driver downloads

No more brittle selectors or verbose method chains

No more tangled imports or platform-specific hacks

3. Architecture
SeleniumBrowser: the symbolic runtime layer. Handles setup, profile cloning, navigation, and exposes Selenium primitives.

PySBK: the declarative interface. Wraps Selenium’s sprawl into clean, intention-driven methods like isClickable(), hasText(), go(), type(), etc.

Modular support files: platform detection, config loading, dependency resolution.

4. Key Features
🔧 Self-resolving dependencies (optional venv builder)

🧠 Symbolic condition matching (expect() with regex, partial, exact, etc.)

🧭 Profile cloning and reuse

🕵️‍♂️ DOM introspection and JS injection

🧱 Unified method naming (click(), type(), get_text())

🧬 Headless and app mode support

🧠 Declarative navigation (go() with reinjection and redirect tracking)

5. Getting Started

Bash
pip install pysbk

Python
from PySBK import PySBK

copilot = PySBK(URL="https://copilot.microsoft.com", browser="Brave", headless=False)
copilot.go()
copilot.wait(copilot.isText(copilot.By.CLASS_NAME, "welcome", "Hello"))
copilot.click(copilot.By.ID, "start")

6. Use Cases
Build browser-native agents

DOM introspection and automation

App prototyping with symbolic flows

Cognitive relay systems (e.g. Copilot integration, Obsidian sync)

7. Philosophy
PySBK is built for developers who value clarity, modularity, and authorship. It’s designed to survive platform revocation, browser mutations, and cognitive drift. It’s not just a tool—it’s a ritual.