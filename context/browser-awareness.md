# Browser Agents

## Available Browser Agents

| Agent | Use For | Example Triggers |
|-------|---------|--------------------|
| `browser-tester:browser-operator` | General automation: navigation, forms, data extraction, screenshots, UX testing | "Go to github.com", "Fill the contact form", "Test the login flow" |
| `browser-tester:browser-researcher` | Research: multi-page exploration, data synthesis, documentation lookup | "Research pricing of top 3 CRM competitors", "Find API rate limits from Stripe docs" |
| `browser-tester:visual-documenter` | Visual documentation: screenshots, QA evidence, change tracking, responsive testing | "Screenshot landing page at different viewports", "Document the checkout flow" |

## When to Use Browser Agents vs web_fetch

| Need | Use | Why |
|------|-----|-----|
| JavaScript rendering (SPAs, React, Vue) | Browser agent | Needs real browser engine |
| Form filling, clicking, navigation | Browser agent | Needs user interaction |
| Screenshots, visual verification | Browser agent | Needs rendering engine |
| Quick HTML/text retrieval from static pages | `web_fetch` | Faster, no browser overhead |
| API calls, JSON endpoints | `web_fetch` | Simpler, direct HTTP |

Agents require `agent-browser` CLI to be installed: `npm install -g agent-browser && agent-browser install`

For CLI reference, troubleshooting, and detailed workflow patterns, use `load_skill(skill_name='browser-reference')`.
