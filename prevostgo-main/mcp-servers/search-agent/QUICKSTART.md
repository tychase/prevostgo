# PrevostGo MCP Search Agent - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Prerequisites
- Node.js 18+ installed
- PrevostGo backend running on http://localhost:8000
- Claude Desktop installed

### Step 1: Install Dependencies
```bash
cd mcp-servers/search-agent
npm install
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env if your API is not on localhost:8000
```

### Step 3: Build the Server
```bash
npm run build
```

### Step 4: Setup Claude Desktop (Automatic)
```bash
npm run setup-claude
```

### Step 5: Restart Claude Desktop
Close and reopen Claude Desktop to load the MCP server.

## 🧪 Testing the Integration

In Claude Desktop, try these commands:

1. **Search for coaches:**
   - "Search for Marathon coaches under $500,000"
   - "Find H3-45 models from 2020 or newer"
   - "Show me coaches with 4 slides in Florida"

2. **Get inventory summary:**
   - "What's the current inventory summary?"
   - "Show me the search facets"

3. **Find similar coaches:**
   - "Find coaches similar to [coach_id]"

## 📝 Manual Claude Desktop Setup (if automatic fails)

1. Open: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add this configuration:
```json
{
  "mcpServers": {
    "prevostgo-search": {
      "command": "node",
      "args": ["C:/Users/tmcha/Dev/prevostgo/mcp-servers/search-agent/dist/index.js"],
      "env": {
        "API_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

3. Restart Claude Desktop

## 🔧 Development Mode

For development with hot reload:
```bash
npm run dev
```

Then update Claude config to use tsx:
```json
{
  "command": "npx",
  "args": ["tsx", "C:/Users/tmcha/Dev/prevostgo/mcp-servers/search-agent/src/index.ts"]
}
```

## 🐛 Troubleshooting

### MCP server not showing in Claude
1. Check Claude Desktop logs: `%APPDATA%\Claude\logs`
2. Verify the path in config is correct
3. Ensure backend is running: `curl http://localhost:8000/api/v1/inventory/summary`

### Search not working
1. Check backend is running
2. Verify API_BASE_URL in .env
3. Check backend logs for errors

### Build errors
1. Ensure Node.js 18+ is installed: `node --version`
2. Clear node_modules and reinstall: `rm -rf node_modules && npm install`

## 📚 Next Steps

1. Explore other MCP capabilities:
   - Add more search filters
   - Implement saved searches
   - Add analytics tools

2. Create additional MCP servers:
   - Lead management agent
   - Inventory management agent
   - Analytics agent

3. Check the main README for architecture details
