# agent-browser Complete Reference

Comprehensive reference for the agent-browser CLI. This document is loaded by browser agents on demand.

## Philosophy: Be a User, Not a Script

When testing web applications, **think and act like a real user**, not a test script:

1. **Explore naturally** - Scroll to see content, click on things to understand them
2. **Be curious** - "What does this button do?" "What happens if I scroll down?"
3. **Communicate what you see** - Describe the UI state to the user as you go
4. **Ask when stuck** - If you can't tell what's happening, ask the user (they may be watching the browser)

### What NOT to Do
- Don't take screenshots reflexively after every action
- Don't poll silently without communicating progress
- Don't execute minimal paths without exploring
- Don't assume you know the UI without looking around

### What TO Do
- Scroll to see all content before concluding
- Click on elements to understand app state
- Tell the user what you're doing during waits
- Ask the user when you're unsure if something completed

## The Ref-Based Approach

agent-browser uses a unique "ref-based" element selection:

1. Run `agent-browser snapshot -ic` to get the accessibility tree
2. Each interactive element gets a ref like `@e1`, `@e2`, `@e3`
3. Use these refs in subsequent commands: `click @e3`, `fill @e5 "text"`

This is more reliable than CSS selectors because:
- Refs are based on the accessibility tree (what screen readers see)
- They're deterministic for the current page state
- They work regardless of CSS class names or DOM structure

**Token savings**: A compact interactive snapshot uses ~700 tokens vs ~10,000+ for full DOM.

## Complete Command Reference

### Lifecycle
| Command | Description |
|---------|-------------|
| `open <url>` | Navigate to URL |
| `open <url> --headed` | Open with visible browser window |
| `close` | Close browser session |

### Inspection
| Command | Description |
|---------|-------------|
| `snapshot -ic` | Interactive + compact (ALWAYS use this) |
| `snapshot -i` | Interactive elements only (less compact) |
| `snapshot` | Full tree (AVOID - wastes tokens on large pages) |
| `snapshot -i -s "selector"` | Scoped to CSS selector |
| `snapshot -i -d 5` | Limit depth to 5 levels |
| `snapshot --json` | JSON output |
| `screenshot <file>` | Capture page |
| `screenshot <file> --full` | Full page capture |

### Interaction
| Command | Description |
|---------|-------------|
| `click @ref` | Click element |
| `dblclick @ref` | Double-click |
| `fill @ref "text"` | Fill input |
| `type @ref "text"` | Type into element (char by char) |
| `press <Key>` | Press key (Enter, Tab, Escape) |
| `select @ref "opt"` | Select dropdown |
| `check @ref` | Check checkbox |
| `uncheck @ref` | Uncheck checkbox |
| `hover @ref` | Hover over element |
| `focus @ref` | Focus element |
| `scroll up/down` | Scroll page |
| `scroll down 1000` | Scroll by pixels |
| `upload @ref "/path"` | Upload file |

### Data Extraction
| Command | Description |
|---------|-------------|
| `get text @ref` | Element text |
| `get html @ref` | Element HTML |
| `get value @ref` | Input value |
| `get attr @ref name` | Attribute value |
| `get title` | Page title |
| `get url` | Current URL |
| `get count "selector"` | Count elements |

### State Checks
| Command | Description |
|---------|-------------|
| `is visible @ref` | Visibility check |
| `is enabled @ref` | Enabled check |
| `is checked @ref` | Checkbox state |

### Navigation
| Command | Description |
|---------|-------------|
| `back` | Browser back |
| `reload` | Reload page |
| `wait 2000` | Wait milliseconds |
| `wait --text "text"` | Wait for text to appear |
| `wait --url "**/path"` | Wait for URL pattern |
| `wait --load networkidle` | Wait for network idle |
| `wait --load domcontentloaded` | Wait for DOM ready |

### Sessions & Profiles
| Command | Description |
|---------|-------------|
| `--session name open <url>` | Named session (isolated cookies) |
| `--profile ~/.path open <url>` | Persistent profile (auth preserved) |
| `session list` | List active sessions |
| `set viewport 1920 1080` | Set viewport size |
| `set device "iPhone 14"` | Emulate device |

### Advanced
| Command | Description |
|---------|-------------|
| `eval "js code"` | Execute JavaScript (page context only, use on trusted sites) |
| `console --json` | View console messages |
| `errors --json` | View page errors |
| `trace start file.zip` | Start recording trace |
| `trace stop` | Stop recording |
| `dialog accept` | Accept dialog |
| `dialog dismiss` | Dismiss dialog |
| `network requests --json` | View network requests |
| `--debug open <url>` | Debug mode |

### Cloud Providers
| Provider | Environment Variables |
|----------|----------------------|
| Browserbase | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| Browser Use | `BROWSER_USE_API_KEY` |
| Kernel | `KERNEL_PROFILE_NAME` |

Usage: `agent-browser -p browserbase open <url>`

## Common Workflow Patterns

### Login with Persistent Profile
```bash
agent-browser --profile ~/.myapp-profile open https://app.example.com/login
agent-browser snapshot -ic
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser close

# Later: reuse authenticated session
agent-browser --profile ~/.myapp-profile open https://app.example.com/dashboard
# Already logged in!
```

### Multi-Account Testing
```bash
# Admin session
agent-browser --session admin open app.com/login
agent-browser snapshot -ic
agent-browser fill @e1 "admin@example.com"
agent-browser fill @e2 "admin-pass"
agent-browser click @e3

# User session (parallel)
agent-browser --session user open app.com/login
agent-browser snapshot -ic
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "user-pass"
agent-browser click @e3

# Test admin vs user access
agent-browser --session admin open app.com/admin
agent-browser --session user open app.com/admin   # Should show "Access Denied"
```

### Multi-Page Form Flow
```bash
# Step 1
agent-browser open https://app.example.com/signup/step1
agent-browser snapshot -ic
agent-browser fill @e1 "John Doe"
agent-browser fill @e2 "john@example.com"
agent-browser click @e3
agent-browser wait --url "**/step2"

# Step 2
agent-browser snapshot -ic
agent-browser fill @e1 "123 Main St"
agent-browser select @e3 "NY"
agent-browser click @e5
agent-browser wait --url "**/step3"

# Step 3
agent-browser snapshot -ic
agent-browser fill @e1 "4111111111111111"
agent-browser click @e4
agent-browser wait --text "Thank you"
agent-browser screenshot confirmation.png
```

### Web Scraping with Infinite Scroll
```bash
agent-browser open https://app.example.com/feed
agent-browser snapshot -ic
# Extract initial items...

agent-browser scroll down 1000
sleep 2
agent-browser snapshot -ic
# Extract new items...

# Repeat as needed
```

### Visual Regression Testing
```bash
# Capture baselines
agent-browser open https://myapp.com/home
agent-browser screenshot baselines/home.png --full

# After deployment, capture current state
agent-browser open https://myapp.com/home
agent-browser screenshot current/home.png --full

# Compare (agent can analyze differences)
```

### File Upload
```bash
agent-browser open https://app.example.com/upload
agent-browser snapshot -ic
agent-browser upload @e1 "/path/to/document.pdf"
agent-browser click @e2    # Submit
agent-browser wait --text "Upload successful"
```

## Screenshots: Strategic Usage

**Screenshots are opt-in, not default.** Only take them when there's a clear reason.

### When Screenshots ARE Useful
| Scenario | Why |
|----------|-----|
| User explicitly requests visual evidence | They asked for it |
| Documenting a bug or unexpected behavior | Need proof |
| Before/after comparison for a specific change | Demonstrating impact |
| Creating documentation or reports | Visual artifacts needed |

### When to Skip Screenshots
| Scenario | Why |
|----------|-----|
| After every click/action | Noise, wastes time |
| During polling/waiting | Same state captured multiple times |
| When user is watching --headed browser | They can see it themselves |
| For routine verification | Snapshot text is sufficient |

## Token Efficiency Best Practices

1. **Always use `-i` flag** for snapshots (interactive elements only): ~700 tokens vs ~10,000
2. **Add `-c` flag** for compact mode: removes empty structural nodes
3. **Scope with `-s`**: `snapshot -i -s "#main"` when you only need part of the page
4. **Limit depth**: `snapshot -i -d 5` for complex pages
5. **Re-snapshot only after changes**: Don't re-snapshot unnecessarily

## Error Handling Patterns

### Retry on Element Not Found
```bash
agent-browser click @e5
# If error: "Element not found"
agent-browser snapshot -ic    # Get fresh refs
agent-browser click @e5       # Retry with new ref
```

### Handle Popup Dialogs
```bash
agent-browser click @e2       # Triggers confirm dialog
agent-browser dialog accept   # Accept it
# Or: agent-browser dialog dismiss
```

## Debugging

1. **Use `--headed` flag** to see the browser window
2. **Check element visibility** before interacting: `agent-browser is visible @e3`
3. **Use full snapshots** when compact misses elements: `agent-browser snapshot` (without -c)
4. **Add delays** for dynamic content: `sleep 2` before snapshot
5. **Enable debug mode**: `agent-browser --debug open <url>`
6. **Check console**: `agent-browser console --json`
7. **Record trace**: `agent-browser trace start trace.zip` then `trace stop`
