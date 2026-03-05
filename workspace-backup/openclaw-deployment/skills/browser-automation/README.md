# Browser Automation Skill

This skill provides comprehensive web automation capabilities using OpenClaw's built-in browser control system.

## Features

### 🌐 Navigation & Control
- Open web pages
- Navigate between URLs
- Refresh pages
- Go back/forward

### 📸 Screenshot & Capture
- Full page screenshots
- Specific element screenshots
- Page snapshots for analysis
- Viewport captures

### 📝 Form Interaction
- Text input filling
- Password field handling
- Button clicking
- Dropdown selection
- Checkbox/radio button handling

### 🔍 Data Extraction
- Text content extraction
- HTML element analysis
- Link collection
- Form data retrieval

## Usage Examples

### Basic Navigation

```bash
# Open a webpage
browser act --action=open --targetUrl="https://example.com"

# Navigate to a specific page
browser act --action=navigate --url="https://example.com/page"

# Take a screenshot
browser act --action=screenshot --fullPage=true

# Take a snapshot to see page structure
browser act --action=snapshot --refs="aria"
```

### Web Scraping

```bash
# Open target page
browser act --action=navigate --url="https://news.example.com"

# Extract headlines
browser act --action=act --kind=evaluate --fn="
  const headlines = document.querySelectorAll('h1, h2, h3');
  return Array.from(headlines).map(h => h.textContent.trim());
"

# Extract all links
browser act --action=act --kind=evaluate --fn="
  const links = document.querySelectorAll('a[href]');
  return Array.from(links).map(a => ({ text: a.textContent, href: a.href }));
"
```

### Form Automation

```bash
# Navigate to login page
browser act --action=navigate --url="https://login.example.com"

# Fill username
browser act --action=act --kind=type --ref="username" --text="your_username"

# Fill password
browser act --action=act --kind=type --ref="password" --text="your_password"

# Submit form
browser act --action=act --kind=click --ref="login-button"
```

## Testing the Skill

Run the example script to test the browser automation capabilities:

```bash
cd ~/oepnclaw/openclaw-main/skills/browser-automation
./example.sh
```

## Safety Guidelines

- **Ethical Use**: Only automate tasks you have permission to perform
- **Respect Rate Limits**: Add delays between automated actions
- **Terms of Service**: Always comply with website terms
- **Privacy**: Respect user data and privacy regulations
- **Transparency**: Be transparent about automation when appropriate

## Browser Control Tips

1. **Start Browser Service**: Ensure browser control is running
2. **Use Proper References**: Use `--refs="aria"` for reliable element identification
3. **Add Delays**: Use `sleep` between actions for complex workflows
4. **Error Handling**: Check if elements exist before interacting with them
5. **Clean Up**: Close browser sessions after completing tasks

## Integration with Other Skills

Combine with other skills for powerful workflows:
- **Weather Skill**: Check weather and make decisions based on conditions
- **File System Skill**: Save scraped data to files
- **Process Control Skill**: Manage browser automation workflows

## Error Troubleshooting

If browser automation isn't working:

1. Check if browser service is running: `browser status`
2. Verify network connectivity
3. Check if target website is accessible
4. Look for CAPTCHAs or anti-bot measures
5. Try different element identification methods

## Advanced Usage

For complex automation tasks, create scripts that combine multiple browser actions:

```bash
#!/bin/bash
# Complex automation script
browser act --action=navigate --url="https://target-site.com/login"
browser act --action=act --kind=type --ref="username" --text="user"
browser act --action=act --kind=type --ref="password" --text="pass"
browser act --action=act --kind=click --ref="submit"
sleep 2
browser act --action=screenshot --ref="dashboard"
browser act --action=act --kind=evaluate --fn="document.querySelector('.dashboard').innerHTML;"
```