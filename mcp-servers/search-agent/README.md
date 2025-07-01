# PrevostGo Search Agent MCP Server

An MCP (Model Context Protocol) server that provides search and inventory management capabilities for the PrevostGo platform.

## Features

### Tools
- **search_coaches**: Advanced search with filters for price, year, mileage, models, converters, etc.
- **get_coach_details**: Get detailed information about a specific coach
- **find_similar_coaches**: Find coaches similar to a given coach
- **get_search_suggestions**: Autocomplete suggestions for search queries

### Resources
- **inventory-summary**: Get a summary of the current coach inventory
- **facets**: Get available search filter options with counts

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API URL
```

3. Build the server:
```bash
npm run build
```

4. Run in development:
```bash
npm run dev
```

## MCP Configuration

Add to your Claude Desktop `claude_desktop_config.json`:

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

## Usage Examples

### Search for coaches
```
Use the search_coaches tool to find:
- Marathon coaches under $500k
- H3-45 models from 2020 or newer
- Coaches with 4 slides in Florida
```

### Get coach details
```
Use get_coach_details with a coach ID to get full information including:
- All specifications
- Features list
- Dealer information
- Images and virtual tour links
```

### Find similar coaches
```
Use find_similar_coaches to find alternatives based on:
- Same model
- Same converter
- Similar price range
- Similar year
```

## Development

### Running tests
```bash
npm test
```

### Adding new tools
1. Add the tool definition in `setupHandlers()`
2. Implement the tool logic in the switch statement
3. Update this README with the new tool documentation

## Architecture

This MCP server acts as a bridge between Claude and the PrevostGo backend API, providing:
- Structured tool interfaces for search operations
- Resource access for inventory data
- Error handling and validation
- Type-safe request/response handling
