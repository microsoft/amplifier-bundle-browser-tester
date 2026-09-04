# amplifier-bundle-browser-tester

Browser automation and testing bundle for [Amplifier](https://github.com/microsoft/amplifier) using [agent-browser](https://github.com/vercel-labs/agent-browser).

## What This Does

Adds browser automation capabilities to any Amplifier session:

- **browser-operator** - General browser automation (navigation, forms, screenshots, UX testing)
- **browser-researcher** - Multi-page research and data extraction
- **visual-documenter** - Screenshot documentation, QA evidence, responsive testing

## Quick Start

### Prerequisites

```bash
# Install agent-browser CLI (requires Node.js 18+)
npm install -g agent-browser

# Download Chromium
agent-browser install

# Linux only: system dependencies
agent-browser install --with-deps
```

### Use as Active Bundle

```bash
amplifier bundle add ./bundle.md --name browser-tester
amplifier bundle use browser-tester
amplifier
```

### Include in Your Bundle

```yaml
# your-bundle.md frontmatter
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-browser-tester@main
```

### Use the Behavior Only

```yaml
# your-behavior.yaml
includes:
  - bundle: browser-tester:behaviors/browser
```

## Agents

| Agent | Purpose | Example |
|-------|---------|---------|
| `browser-operator` | General automation | "Go to github.com and find trending repos" |
| `browser-researcher` | Research & extraction | "Research pricing of top 3 CRM competitors" |
| `visual-documenter` | Screenshots & docs | "Screenshot landing page at different viewports" |

## Recipes

| Recipe | Purpose |
|--------|---------|
| `competitive-research` | Research competitors and produce comparison reports |
| `form-automation` | Automate form filling with provided data |
| `visual-audit` | Capture screenshots across multiple pages |

### Example Recipes

| Recipe | Purpose |
|--------|---------|
| `quick-demo` | Quick browser automation demo |
| `verify-deployed-app` | Verify a deployed app works |
| `check-status-page` | Check a status page |
| `extract-dynamic-content` | Extract content from JS-heavy pages |
| `monitor-competitor-pricing` | Monitor competitor pricing changes |

Every shipped recipe declares `schema_version: 2` and a `dependencies:` block,
so its `agent:` references resolve from the recipe's own declared closure rather
than from whatever session bundle invoked it. That is what makes these recipes
runnable from *any* bundle, not just one that already carries browser-tester.

## Tests

```bash
pytest tests/
```

`tests/test_recipe_manifests.py` enforces the rule above: any recipe under
`recipes/` that references a namespaced agent must declare that agent in its own
manifest. It imports only `pytest` and `PyYAML`.

## Architecture

This bundle follows the **context sink pattern**:

- **Root session** gets thin awareness (~70 lines) via `context.include`
- **Agents** carry heavy documentation (~1000+ lines) loaded only on spawn
- Works when used directly, as an app bundle, or composed into other bundles

## Attribution

This bundle consolidates work from:
- [ramparte/amplifier-bundle-browser](https://github.com/ramparte/amplifier-bundle-browser) (Apache-2.0)
- [samueljklee/amplifier-bundle-browser](https://github.com/samueljklee/amplifier-bundle-browser) (MIT)

See [NOTICE](NOTICE) for full attribution.

## Contributing

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
## License

MIT - See [LICENSE](LICENSE)
