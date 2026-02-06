# Composed Bundle Test Scenarios

## Scenario 1: Browser awareness survives composition
Prompt: "What browser tools do I have available?"
Expected: Agent knows about browser-tester agents from context.include (NOT from bundle.md body which was replaced)

## Scenario 2: Install instructions survive composition
Prompt: "How do I set up browser automation?"
Expected: Agent provides npm install instructions from browser-awareness.md

## Scenario 3: Agent delegation works
Prompt: "Test the login page at https://example.com"
Expected: Agent delegates to browser-tester:browser-operator
