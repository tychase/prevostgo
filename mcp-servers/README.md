# PrevostGo MCP Architecture

This directory contains Model Context Protocol (MCP) servers that enable Claude Desktop to interact with the PrevostGo platform.

## 🏗️ Architecture Overview

```
mcp-servers/
├── search-agent/          # Search and inventory browsing
├── lead-agent/           # Lead management (coming soon)
├── inventory-agent/      # Inventory management (coming soon)
└── analytics-agent/      # Analytics and reporting (coming soon)
```

## 🚀 Current MCP Servers

### 1. Search Agent (✅ Ready)
The search agent provides comprehensive search functionality for browsing Prevost coaches.

**Features:**
- Advanced search with multiple filters
- Coach details retrieval
- Similar coach recommendations
- Search suggestions/autocomplete
- Inventory summaries and facets

**Quick Start:**
```bash
cd search-agent
npm install
npm run build
npm run setup-claude
# Restart Claude Desktop
```

### 2. Lead Agent (🚧 Coming Soon)
Will handle lead management, scoring, and CRM functionality.

**Planned Features:**
- Lead creation and updates
- Lead scoring and qualification
- Search alert management
- Lead activity tracking

### 3. Inventory Agent (🚧 Coming Soon)
Will provide inventory management capabilities.

**Planned Features:**
- Add/update coach listings
- Bulk import functionality
- Price management
- Inventory analytics

### 4. Analytics Agent (🚧 Coming Soon)
Will provide reporting and analytics capabilities.

**Planned Features:**
- Sales analytics
- Lead conversion metrics
- Inventory performance
- Custom report generation

## 🔧 Development Guidelines

### Creating a New MCP Server

1. **Create the directory structure:**
```bash
mkdir mcp-servers/your-agent
cd mcp-servers/your-agent
npm init -y
```

2. **Install MCP SDK:**
```bash
npm install @modelcontextprotocol/sdk axios dotenv
npm install -D typescript tsx @types/node
```

3. **Use the search-agent as a template:**
- Copy `tsconfig.json`
- Copy the basic structure from `src/index.ts`
- Adapt the tools and resources for your use case

4. **Follow MCP patterns:**
- Use tools for actions (POST, PUT, DELETE)
- Use resources for data access (GET)
- Provide clear descriptions for Claude
- Handle errors gracefully

### Best Practices

1. **Tool Design:**
   - Make tools focused and single-purpose
   - Use descriptive names and descriptions
   - Provide comprehensive input schemas
   - Return structured, parseable responses

2. **Error Handling:**
   - Always wrap API calls in try-catch
   - Provide meaningful error messages
   - Use appropriate MCP error codes
   - Log errors for debugging

3. **Configuration:**
   - Use environment variables for configuration
   - Provide .env.example files
   - Document all configuration options
   - Support both development and production modes

4. **Documentation:**
   - Include README with setup instructions
   - Provide usage examples
   - Document all tools and resources
   - Include troubleshooting guides

## 🧪 Testing MCP Servers

### Manual Testing with Claude Desktop

1. Install and configure the MCP server
2. Restart Claude Desktop
3. Ask Claude to use the tools:
   - "Search for Marathon coaches under $500k"
   - "Get details about coach [ID]"
   - "Find similar coaches to [ID]"

### Integration Testing

Each MCP server should include integration tests:

```bash
npm run test:integration
```

This verifies:
- Backend connectivity
- Tool functionality
- Response formats
- Error handling

## 📝 MCP Configuration Reference

Claude Desktop configuration location:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Example configuration:
```json
{
  "mcpServers": {
    "prevostgo-search": {
      "command": "node",
      "args": ["C:/path/to/search-agent/dist/index.js"],
      "env": {
        "API_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

## 🔍 Debugging

### Enable MCP logging in Claude Desktop:
1. Check logs at: `%APPDATA%\Claude\logs`
2. Look for MCP-related errors
3. Verify server is starting correctly

### Common Issues:
- **Server not appearing:** Check path in config
- **Tools not working:** Verify backend is running
- **Errors in responses:** Check server logs with `console.error`

## 🚀 Future Enhancements

1. **Unified MCP Gateway:**
   - Single MCP server routing to multiple services
   - Shared authentication
   - Cross-service operations

2. **Advanced Features:**
   - WebSocket support for real-time updates
   - File upload/download capabilities
   - Batch operations
   - Caching layer

3. **Claude-Specific Optimizations:**
   - Context-aware responses
   - Progressive disclosure of information
   - Smart defaults based on conversation

## 📚 Resources

- [MCP Documentation](https://github.com/anthropics/model-context-protocol)
- [Claude Desktop Docs](https://claude.ai/desktop)
- [PrevostGo API Docs](../backend/README.md)
