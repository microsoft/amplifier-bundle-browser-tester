# Active Bundle Test Scenarios

## Scenario 1: Basic Navigation
Prompt: "Go to https://example.com and tell me what's on the page"
Expected: Agent uses browser-operator, opens page, describes content

## Scenario 2: Screenshot Request  
Prompt: "Take a screenshot of https://github.com at desktop and mobile sizes"
Expected: Agent delegates to visual-documenter

## Scenario 3: Research Task
Prompt: "Research the pricing of Vercel, Netlify, and Cloudflare Pages"
Expected: Agent delegates to web-researcher

## Scenario 4: Missing agent-browser
Prompt: "Go to example.com" (with agent-browser NOT installed)
Expected: Agent detects missing dependency, provides install instructions

## Scenario 5: Form Filling
Prompt: "Go to https://httpbin.org/forms/post and fill out the form with test data"
Expected: Agent uses browser-operator, fills form fields
