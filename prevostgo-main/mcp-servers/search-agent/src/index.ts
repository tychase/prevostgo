import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListToolsRequestSchema,
  CallToolRequestSchema,
  ErrorCode,
  McpError
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Types for our search functionality
interface SearchFilters {
  price_min?: number;
  price_max?: number;
  year_min?: number;
  year_max?: number;
  mileage_max?: number;
  models?: string[];
  converters?: string[];
  slide_counts?: number[];
  conditions?: string[];
  must_have_features?: string[];
  dealer_states?: string[];
  sort_by?: string;
  sort_order?: string;
  page?: number;
  per_page?: number;
}

interface Coach {
  id: string;
  title: string;
  year: number;
  model?: string;
  chassis_type?: string;
  converter?: string;
  condition: string;
  price?: number;
  price_display?: string;
  mileage?: number;
  engine?: string;
  slide_count: number;
  features: string[];
  images: string[];
  dealer_name?: string;
  dealer_state?: string;
}

class PrevostGoSearchServer {
  private server: Server;
  
  constructor() {
    this.server = new Server({
      name: 'prevostgo-search',
      version: '0.1.0'
    }, {
      capabilities: {
        resources: { list: true, read: true },
        tools: { list: true, call: true }
      }
    });
    
    this.setupHandlers();
  }
  
  private setupHandlers() {
    // Handle resource listing
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [
          {
            uri: 'search://inventory-summary',
            name: 'Inventory Summary',
            description: 'Get a summary of the current coach inventory',
            mimeType: 'application/json'
          },
          {
            uri: 'search://facets',
            name: 'Search Facets',
            description: 'Get available search filter options with counts',
            mimeType: 'application/json'
          }
        ]
      };
    });
    
    // Handle resource reading
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      
      try {
        if (uri === 'search://inventory-summary') {
          const response = await axios.get(`${API_BASE_URL}/api/inventory/summary`);
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(response.data, null, 2)
            }]
          };
        } else if (uri === 'search://facets') {
          const response = await axios.get(`${API_BASE_URL}/api/search/facets`);
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(response.data, null, 2)
            }]
          };
        }
        
        throw new McpError(ErrorCode.InvalidRequest, `Unknown resource: ${uri}`);
      } catch (error) {
        if (error instanceof McpError) throw error;
        throw new McpError(
          ErrorCode.InternalError, 
          `Failed to fetch resource: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    });
    
    // Handle tool listing
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'search_coaches',
            description: 'Search for Prevost coaches with advanced filters',
            inputSchema: {
              type: 'object',
              properties: {
                price_min: { type: 'number', description: 'Minimum price in dollars' },
                price_max: { type: 'number', description: 'Maximum price in dollars' },
                year_min: { type: 'number', description: 'Minimum year' },
                year_max: { type: 'number', description: 'Maximum year' },
                mileage_max: { type: 'number', description: 'Maximum mileage' },
                models: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: 'Filter by coach models (e.g., H3-45, XLII)'
                },
                converters: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: 'Filter by converters (e.g., Marathon, Liberty)'
                },
                slide_counts: { 
                  type: 'array', 
                  items: { type: 'number' },
                  description: 'Filter by number of slides'
                },
                conditions: { 
                  type: 'array', 
                  items: { type: 'string', enum: ['new', 'pre-owned'] },
                  description: 'Filter by condition'
                },
                must_have_features: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: 'Required features'
                },
                dealer_states: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: 'Filter by dealer location states'
                },
                sort_by: { 
                  type: 'string', 
                  enum: ['price', 'year', 'mileage', 'created_at'],
                  default: 'price',
                  description: 'Sort field'
                },
                sort_order: { 
                  type: 'string', 
                  enum: ['asc', 'desc'],
                  default: 'asc',
                  description: 'Sort order'
                },
                page: { type: 'number', default: 1, description: 'Page number' },
                per_page: { type: 'number', default: 20, description: 'Results per page' }
              }
            }
          },
          {
            name: 'get_coach_details',
            description: 'Get detailed information about a specific coach',
            inputSchema: {
              type: 'object',
              properties: {
                coach_id: { type: 'string', description: 'The ID of the coach' }
              },
              required: ['coach_id']
            }
          },
          {
            name: 'find_similar_coaches',
            description: 'Find coaches similar to a given coach',
            inputSchema: {
              type: 'object',
              properties: {
                coach_id: { type: 'string', description: 'The ID of the reference coach' },
                limit: { type: 'number', default: 6, description: 'Maximum number of similar coaches to return' }
              },
              required: ['coach_id']
            }
          },
          {
            name: 'get_search_suggestions',
            description: 'Get autocomplete suggestions for search',
            inputSchema: {
              type: 'object',
              properties: {
                query: { type: 'string', description: 'The search query' },
                field: { 
                  type: 'string', 
                  enum: ['all', 'model', 'converter', 'location'],
                  default: 'all',
                  description: 'Field to search in'
                }
              },
              required: ['query']
            }
          }
        ]
      };
    });
    
    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        switch (name) {
          case 'search_coaches': {
            const filters: SearchFilters = args as SearchFilters;
            const response = await axios.post(`${API_BASE_URL}/api/search/coaches`, filters);
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2)
                }]
              }
            };
          }
          
          case 'get_coach_details': {
            const { coach_id } = args as { coach_id: string };
            const response = await axios.get(`${API_BASE_URL}/api/inventory/coaches/${coach_id}`);
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2)
                }]
              }
            };
          }
          
          case 'find_similar_coaches': {
            const { coach_id, limit = 6 } = args as { coach_id: string; limit?: number };
            const response = await axios.post(
              `${API_BASE_URL}/api/search/similar/${coach_id}?limit=${limit}`
            );
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2)
                }]
              }
            };
          }
          
          case 'get_search_suggestions': {
            const { query, field = 'all' } = args as { query: string; field?: string };
            const response = await axios.get(
              `${API_BASE_URL}/api/search/suggestions?q=${encodeURIComponent(query)}&field=${field}`
            );
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2)
                }]
              }
            };
          }
          
          default:
            throw new McpError(ErrorCode.InvalidRequest, `Unknown tool: ${name}`);
        }
      } catch (error) {
        if (error instanceof McpError) throw error;
        
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        const errorDetails = axios.isAxiosError(error) 
          ? JSON.stringify(error.response?.data || error.message)
          : errorMessage;
          
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${errorDetails}`
        );
      }
    });
  }
  
  async start() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('PrevostGo Search MCP Server started');
  }
}

// Start the server
const server = new PrevostGoSearchServer();
server.start().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});
