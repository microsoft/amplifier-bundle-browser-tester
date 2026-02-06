---
bundle:
  name: browser-tester
  version: 1.0.0
  description: Browser automation and testing for AI agents using agent-browser

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: browser-tester:behaviors/browser

skills:
  dirs:
    - git+https://github.com/robotdad/skills@main#subdirectory=image-vision
---

# Browser Tester

Browser automation for AI agents using [agent-browser](https://github.com/vercel-labs/agent-browser).

## Capabilities

- Navigate, interact with, and test web pages using a real browser
- Fill forms, click buttons, extract structured data
- Take screenshots for QA, documentation, and visual regression
- Handle SPAs and JavaScript-heavy applications (React, Vue, Angular)
- Session isolation and persistent authentication profiles

## Requirements

agent-browser must be installed before using this bundle:

```bash
# Install CLI (requires Node.js 18+)
npm install -g agent-browser

# Download Chromium
agent-browser install

# Linux only: system dependencies
agent-browser install --with-deps
```

@browser-tester:context/browser-awareness.md

---

@foundation:context/shared/common-system-base.md
