---
name: browser-automation
description: "Browser automation and web interaction skills. Use for web scraping, form filling, automated navigation, and interactive web tasks. NOT for: automated commenting, spam, or malicious automation."
homepage: https://docs.openclaw.ai/skills/browser-automation
metadata: { "openclaw": { "emoji": "🌐", "requires": { "bins": ["curl"], "tools": ["browser"] } } }
---

# Browser Automation Skill

Provides web automation capabilities using OpenClaw's built-in browser control. Can perform web scraping, form filling, navigation, and interactive tasks.

## When to Use

✅ **USE this skill when:**

- "Scrape data from website"
- "Fill out web forms automatically"
- "Automate web navigation"
- "Take screenshots of web pages"
- "Extract information from web pages"
- "Login to websites automatically"
- "Monitor website changes"

## When NOT to Use

❌ **DON'T use this skill when:**

- Automated spam or malicious activities
- Circumventing website anti-bot measures
- Posting comments or content automatically (unless explicitly allowed)
- DDoS or flood attacks
- Violating website terms of service
- Password guessing or brute force attacks

## Browser Control Functions

### Navigation

```bash
# Open webpage
browser act --action=open --targetUrl="https://example.com"

# Navigate to URL
browser act --action=navigate --url="https://example.com/page"

# Refresh page
browser act --action=act --kind=click --ref="refresh-button"

# Go back/forward
browser act --action=act --kind=click --ref="back-button"
```

### Screenshot Operations

```bash
# Take full page screenshot
browser act --action=screenshot --fullPage=true

# Take viewport screenshot
browser act --action=screenshot

# Take screenshot of specific element
browser act --action=screenshot --ref="main-content"
```

### Form Interactions

```bash
# Fill text input
browser act --action=act --kind=type --ref="username" --text="myuser"

# Fill password
browser act --action=act --kind=type --ref="password" --text="mypassword"

# Click buttons
browser act --action=act --kind=click --ref="submit-button"

# Select dropdown
browser act --action=act --kind=select --ref="country-select" --values="US"
```

### Data Extraction

```bash
# Take snapshot for element references
browser act --action=snapshot

# Wait for element
browser act --action=act --kind=wait --ref="load-button" --timeMs=5000

# Get page content
browser act --action=snapshot --depth=3
```

## Web Scraping Templates

### Basic Page Scraping

```bash
# Open page and take snapshot
browser act --action=open --targetUrl="https://example.com"
browser act --action=snapshot --depth=2

# Extract text content
browser act --action=act --kind=evaluate --fn="
  const title = document.title;
  const content = document.body.textContent;
  return { title, content };
"
```

### Form Automation

```bash
# Navigate to login page
browser act --action=navigate --url="https://example.com/login"

# Fill login form
browser act --action=act --kind=type --ref="username" --text="your_username"
browser act --action=act --kind=type --ref="password" --text="your_password"

# Submit form
browser act --action=act --kind=click --ref="login-button"
```

### Automated Task

```bash
# Open dashboard
browser act --action=navigate --url="https://dashboard.example.com"

# Wait for page load
browser act --action=act --kind=wait --timeMs=3000

# Click navigation menu
browser act --action=act --kind=click --ref="reports-menu"

# Take screenshot of reports page
browser act --action=screenshot --ref="reports-container"
```

## Quick Responses

**"Take screenshot of webpage"**

```bash
browser act --action=open --targetUrl="https://example.com"
browser act --action=screenshot
```

**"Extract all links from page"**

```bash
browser act --action=navigate --url="https://example.com"
browser act --action=act --kind=evaluate --fn="Array.from(document.querySelectorAll('a')).map(a => a.href);"
```

**"Automated login"**

```bash
browser act --action=navigate --url="https://login.example.com"
browser act --action=act --kind=type --ref="username" --text="your_username"
browser act --action=act --kind=type --ref="password" --text="your_password"
browser act --action=act --kind=click --ref="submit"
```

## Notes

- Always respect website robots.txt and terms of service
- Use appropriate delays between actions to avoid overwhelming servers
- Consider user impact when automating public websites
- Clean up browser sessions after automation tasks
- Monitor for CAPTCHAs and handle them appropriately

## Safety Guidelines

- **Ethical Use**: Only automate tasks you have permission to automate
- **Rate Limiting**: Add delays between requests
- **Data Privacy**: Respect user data and privacy
- **Impact Assessment**: Consider your automation's impact on target systems
- **Transparency**: Be transparent about automation when appropriate

## Examples

**"Scrape product information"**

```bash
# Open product page
browser act --action=navigate --url="https://shop.example.com/products/123"

# Extract product details
browser act --action=act --kind=evaluate --fn="
  const product = {
    name: document.querySelector('h1').textContent,
    price: document.querySelector('.price').textContent,
    description: document.querySelector('.description').textContent
  };
  return product;
"
```

**"Monitor for changes"**

```bash
# Take baseline screenshot
browser act --action=navigate --url="https://monitor.example.com"
browser act --action=screenshot --ref="main-content"

# Wait and check for changes
sleep 300 # Wait 5 minutes
browser act --action=snapshot --ref="main-content"
```