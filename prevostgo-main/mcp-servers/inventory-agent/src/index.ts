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
import FormData from 'form-data';
import { parse } from 'csv-parse/sync';
import fs from 'fs';
import path from 'path';

// Load environment variables
dotenv.config();

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const PYTHON_EXECUTABLE = process.env.PYTHON_EXECUTABLE || 'python';
const SCRAPER_PATH = process.env.SCRAPER_PATH || 'C:\\Users\\tmcha\\Dev\\prevostgo\\backend\\scraper_final_v2.py';

// Types for our inventory functionality
interface Coach {
  id?: string;
  title: string;
  year: number;
  model?: string;
  chassis_type?: string;
  converter?: string;
  condition: 'new' | 'pre-owned';
  price?: number;
  price_display?: string;
  price_status?: string;
  mileage?: number;
  engine?: string;
  slide_count?: number;
  features?: string[];
  images?: string[];
  dealer_name?: string;
  dealer_state?: string;
  dealer_phone?: string;
  dealer_email?: string;
  listing_url?: string;
  source?: string;
  status?: string;
}

interface InventoryStats {
  total_coaches: number;
  available_coaches: number;
  sold_coaches: number;
  coaches_with_prices: number;
  average_price?: number;
  by_converter: Record<string, number>;
  by_model: Record<string, number>;
  by_year: Record<string, number>;
  last_scrape?: string;
}

class PrevostGoInventoryServer {
  private server: Server;
  
  constructor() {
    this.server = new Server({
      name: 'prevostgo-inventory',
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
            uri: 'inventory://database-stats',
            name: 'Database Statistics',
            description: 'Get current database statistics and inventory health',
            mimeType: 'application/json'
          },
          {
            uri: 'inventory://scraper-status',
            name: 'Scraper Status',
            description: 'Get the last scraper run status and statistics',
            mimeType: 'application/json'
          },
          {
            uri: 'inventory://data-quality',
            name: 'Data Quality Report',
            description: 'Analyze data quality and identify missing information',
            mimeType: 'application/json'
          }
        ]
      };
    });
    
    // Handle resource reading
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      
      try {
        if (uri === 'inventory://database-stats') {
          // Get inventory summary from API
          const response = await axios.get(`${API_BASE_URL}/api/inventory/summary`);
          
          // Calculate additional stats
          const stats: InventoryStats = {
            total_coaches: response.data.total_coaches,
            available_coaches: response.data.total_coaches,
            sold_coaches: 0, // Would need to query separately
            coaches_with_prices: Object.values(response.data.price_ranges)
              .reduce((sum: number, count: any) => sum + (count === 'contact_for_price' ? 0 : count), 0),
            by_converter: response.data.by_converter,
            by_model: response.data.by_model,
            by_year: response.data.by_year
          };
          
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(stats, null, 2)
            }]
          };
        } else if (uri === 'inventory://scraper-status') {
          // Would need to implement scraper status tracking
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify({
                last_run: 'Check database for last scraped_at timestamp',
                status: 'Ready to run',
                message: 'Use run_scraper tool to fetch latest inventory'
              }, null, 2)
            }]
          };
        } else if (uri === 'inventory://data-quality') {
          // Analyze data quality
          const response = await axios.get(`${API_BASE_URL}/api/inventory/?per_page=1000`);
          const coaches = response.data.coaches;
          
          const quality = {
            total_coaches: coaches.length,
            missing_prices: coaches.filter((c: any) => !c.price).length,
            missing_images: coaches.filter((c: any) => !c.images || c.images.length === 0).length,
            missing_converter: coaches.filter((c: any) => !c.converter || c.converter === 'Unknown').length,
            missing_model: coaches.filter((c: any) => !c.model || c.model === 'Unknown').length,
            missing_dealer_info: coaches.filter((c: any) => !c.dealer_name || c.dealer_name === 'Unknown').length
          };
          
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(quality, null, 2)
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
            name: 'run_scraper',
            description: 'Run the Prevost inventory scraper to fetch latest coaches',
            inputSchema: {
              type: 'object',
              properties: {
                fetch_details: { 
                  type: 'boolean', 
                  default: true,
                  description: 'Fetch detailed info for each listing' 
                },
                limit: { 
                  type: 'number',
                  description: 'Limit number of coaches to scrape (for testing)' 
                }
              }
            }
          },
          {
            name: 'add_coach',
            description: 'Add a new coach to the inventory',
            inputSchema: {
              type: 'object',
              properties: {
                title: { type: 'string', description: 'Coach title/description' },
                year: { type: 'number', description: 'Manufacturing year' },
                model: { type: 'string', description: 'Coach model (e.g., H3-45, XLII)' },
                converter: { type: 'string', description: 'Converter name' },
                condition: { 
                  type: 'string', 
                  enum: ['new', 'pre-owned'],
                  description: 'Coach condition' 
                },
                price: { type: 'number', description: 'Price in dollars' },
                mileage: { type: 'number', description: 'Mileage' },
                slide_count: { type: 'number', description: 'Number of slides' },
                features: { 
                  type: 'array',
                  items: { type: 'string' },
                  description: 'List of features' 
                },
                dealer_name: { type: 'string', description: 'Dealer name' },
                dealer_state: { type: 'string', description: 'Dealer state' },
                dealer_phone: { type: 'string', description: 'Dealer phone' },
                dealer_email: { type: 'string', description: 'Dealer email' }
              },
              required: ['title', 'year', 'condition']
            }
          },
          {
            name: 'update_coach',
            description: 'Update an existing coach in the inventory',
            inputSchema: {
              type: 'object',
              properties: {
                coach_id: { type: 'string', description: 'Coach ID to update' },
                status: { type: 'string', description: 'Status (available, sold, pending)' },
                price: { type: 'number', description: 'Updated price in dollars' },
                price_display: { type: 'string', description: 'Display price text' },
                price_status: { 
                  type: 'string',
                  enum: ['available', 'contact_for_price'],
                  description: 'Price status' 
                }
              },
              required: ['coach_id']
            }
          },
          {
            name: 'bulk_import_csv',
            description: 'Import coaches from a CSV file',
            inputSchema: {
              type: 'object',
              properties: {
                csv_content: { type: 'string', description: 'CSV content as string' },
                dry_run: { 
                  type: 'boolean', 
                  default: false,
                  description: 'Validate without importing' 
                }
              },
              required: ['csv_content']
            }
          },
          {
            name: 'check_duplicates',
            description: 'Check for duplicate coaches in the inventory',
            inputSchema: {
              type: 'object',
              properties: {
                threshold: { 
                  type: 'number', 
                  default: 0.9,
                  description: 'Similarity threshold (0-1)' 
                }
              }
            }
          },
          {
            name: 'fix_data_issues',
            description: 'Automatically fix common data issues',
            inputSchema: {
              type: 'object',
              properties: {
                fix_prices: { 
                  type: 'boolean', 
                  default: true,
                  description: 'Fix price formatting issues' 
                },
                fix_converters: { 
                  type: 'boolean', 
                  default: true,
                  description: 'Standardize converter names' 
                },
                fix_models: { 
                  type: 'boolean', 
                  default: true,
                  description: 'Standardize model names' 
                },
                dry_run: { 
                  type: 'boolean', 
                  default: false,
                  description: 'Preview changes without applying' 
                }
              }
            }
          },
          {
            name: 'export_inventory',
            description: 'Export inventory data in various formats',
            inputSchema: {
              type: 'object',
              properties: {
                format: { 
                  type: 'string',
                  enum: ['csv', 'json', 'excel'],
                  default: 'csv',
                  description: 'Export format' 
                },
                include_sold: { 
                  type: 'boolean', 
                  default: false,
                  description: 'Include sold coaches' 
                },
                fields: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Specific fields to export (default: all)'
                }
              }
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
          case 'run_scraper': {
            const { fetch_details = true, limit } = args as { fetch_details?: boolean; limit?: number };
            
            // Call the API endpoint to trigger scraping
            const response = await axios.post(
              `${API_BASE_URL}/api/inventory/scrape?fetch_details=${fetch_details}${limit ? `&limit=${limit}` : ''}`
            );
            
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify({
                    success: true,
                    message: 'Scraper completed successfully',
                    results: response.data
                  }, null, 2)
                }]
              }
            };
          }
          
          case 'add_coach': {
            const coachData = args as any as Coach;
            
            // Convert price to cents if provided
            if (coachData.price) {
              coachData.price = coachData.price * 100;
            }
            
            // This would need a new endpoint in the backend
            // For now, return a mock response
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify({
                    success: false,
                    message: 'Add coach endpoint not yet implemented in backend',
                    recommendation: 'Use the scraper to import coaches or implement POST /api/inventory/coaches endpoint'
                  }, null, 2)
                }]
              }
            };
          }
          
          case 'update_coach': {
            const { coach_id, ...updateData } = args as any;
            
            const response = await axios.put(
              `${API_BASE_URL}/api/inventory/${coach_id}`,
              updateData
            );
            
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify({
                    success: true,
                    coach: response.data
                  }, null, 2)
                }]
              }
            };
          }
          
          case 'bulk_import_csv': {
            const { csv_content, dry_run = false } = args as { csv_content: string; dry_run?: boolean };
            
            try {
              // Parse CSV
              const records = parse(csv_content, {
                columns: true,
                skip_empty_lines: true
              });
              
              const results = {
                total_rows: records.length,
                valid_coaches: 0,
                errors: [] as string[],
                coaches: [] as any[]
              };
              
              // Validate each record
              for (let i = 0; i < records.length; i++) {
                const record = records[i];
                try {
                  const coach: Coach = {
                    title: record.title || `${record.year} ${record.model} ${record.converter}`.trim(),
                    year: parseInt(record.year) || 0,
                    model: record.model || 'Unknown',
                    converter: record.converter || 'Unknown',
                    condition: record.condition === 'new' ? 'new' : 'pre-owned',
                    price: record.price ? parseInt(record.price) * 100 : undefined,
                    mileage: record.mileage ? parseInt(record.mileage) : undefined,
                    slide_count: record.slide_count ? parseInt(record.slide_count) : 0,
                    dealer_name: record.dealer_name,
                    dealer_state: record.dealer_state,
                    features: record.features ? record.features.split(',').map((f: string) => f.trim()) : []
                  };
                  
                  results.coaches.push(coach);
                  results.valid_coaches++;
                } catch (e) {
                  results.errors.push(`Row ${i + 1}: ${e instanceof Error ? e.message : 'Invalid data'}`);
                }
              }
              
              if (!dry_run && results.valid_coaches > 0) {
                // Would need to implement bulk import endpoint
                return {
                  toolResult: {
                    content: [{
                      type: 'text',
                      text: JSON.stringify({
                        success: false,
                        message: 'Bulk import endpoint not yet implemented',
                        validation_results: results
                      }, null, 2)
                    }]
                  }
                };
              }
              
              return {
                toolResult: {
                  content: [{
                    type: 'text',
                    text: JSON.stringify({
                      success: true,
                      dry_run: true,
                      results
                    }, null, 2)
                  }]
                }
              };
            } catch (error) {
              throw new McpError(
                ErrorCode.InvalidRequest,
                `CSV parsing failed: ${error instanceof Error ? error.message : 'Unknown error'}`
              );
            }
          }
          
          case 'check_duplicates': {
            const { threshold = 0.9 } = args as { threshold?: number };
            
            // Get all coaches
            const response = await axios.get(`${API_BASE_URL}/api/inventory/?per_page=1000`);
            const coaches = response.data.coaches;
            
            const duplicates: any[] = [];
            
            // Simple duplicate detection based on title similarity
            for (let i = 0; i < coaches.length; i++) {
              for (let j = i + 1; j < coaches.length; j++) {
                const similarity = this.calculateSimilarity(
                  coaches[i].title.toLowerCase(),
                  coaches[j].title.toLowerCase()
                );
                
                if (similarity >= threshold) {
                  duplicates.push({
                    coach1: { id: coaches[i].id, title: coaches[i].title },
                    coach2: { id: coaches[j].id, title: coaches[j].title },
                    similarity: similarity.toFixed(2)
                  });
                }
              }
            }
            
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify({
                    total_coaches: coaches.length,
                    duplicate_pairs: duplicates.length,
                    duplicates: duplicates.slice(0, 20) // Limit output
                  }, null, 2)
                }]
              }
            };
          }
          
          case 'fix_data_issues': {
            const { 
              fix_prices = true, 
              fix_converters = true, 
              fix_models = true,
              dry_run = false 
            } = args as any;
            
            // Get all coaches
            const response = await axios.get(`${API_BASE_URL}/api/inventory/?per_page=1000`);
            const coaches = response.data.coaches;
            
            const fixes = {
              price_fixes: 0,
              converter_fixes: 0,
              model_fixes: 0,
              changes: [] as any[]
            };
            
            // Common converter mappings
            const converterMap: Record<string, string> = {
              'marathon': 'Marathon',
              'liberty': 'Liberty', 
              'royale': 'Royale',
              'outlaw': 'Outlaw',
              'millenium': 'Millennium',
              'millennium': 'Millennium',
              'vantare': 'Vantare',
              'show coaches': 'Show Coaches',
              'country coach': 'Country Coach',
              'featherlite': 'Featherlite'
            };
            
            // Model standardization
            const modelMap: Record<string, string> = {
              'h345': 'H3-45',
              'h3 45': 'H3-45',
              'xlii': 'XLII',
              'xl2': 'XLII',
              'xl': 'XL',
              'x3': 'X3-45',
              'x345': 'X3-45'
            };
            
            for (const coach of coaches) {
              const updates: any = {};
              
              // Fix converters
              if (fix_converters && coach.converter) {
                const normalized = coach.converter.toLowerCase().trim();
                if (converterMap[normalized] && converterMap[normalized] !== coach.converter) {
                  updates.converter = converterMap[normalized];
                  fixes.converter_fixes++;
                }
              }
              
              // Fix models
              if (fix_models && coach.model) {
                const normalized = coach.model.toLowerCase().replace(/[^a-z0-9]/g, '');
                if (modelMap[normalized] && modelMap[normalized] !== coach.model) {
                  updates.model = modelMap[normalized];
                  fixes.model_fixes++;
                }
              }
              
              // Fix prices (ensure they're in cents)
              if (fix_prices && coach.price && coach.price < 10000) {
                // Likely in dollars, not cents
                updates.price = coach.price * 100;
                fixes.price_fixes++;
              }
              
              if (Object.keys(updates).length > 0) {
                fixes.changes.push({
                  coach_id: coach.id,
                  title: coach.title,
                  updates
                });
                
                if (!dry_run) {
                  // Apply the fix
                  await axios.put(`${API_BASE_URL}/api/inventory/${coach.id}`, updates);
                }
              }
            }
            
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: JSON.stringify({
                    dry_run,
                    total_coaches: coaches.length,
                    fixes,
                    message: dry_run ? 'Preview mode - no changes applied' : 'Fixes applied successfully'
                  }, null, 2)
                }]
              }
            };
          }
          
          case 'export_inventory': {
            const { format = 'csv', include_sold = false, fields } = args as any;
            
            // Get inventory
            const response = await axios.get(
              `${API_BASE_URL}/api/inventory/?per_page=1000${include_sold ? '' : '&status=available'}`
            );
            const coaches = response.data.coaches;
            
            let output: string;
            
            if (format === 'csv') {
              // Create CSV
              const headers = fields || [
                'id', 'title', 'year', 'model', 'converter', 'condition',
                'price', 'mileage', 'slide_count', 'dealer_name', 'dealer_state'
              ];
              
              const rows = [headers.join(',')];
              
              for (const coach of coaches) {
                const row = headers.map((field: string) => {
                  const value = coach[field];
                  // Handle special formatting
                  if (field === 'price' && value) {
                    return `$${value.toLocaleString()}`;
                  }
                  // Escape CSV values
                  if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                  }
                  return value || '';
                });
                rows.push(row.join(','));
              }
              
              output = rows.join('\n');
            } else {
              // JSON format
              output = JSON.stringify(coaches, null, 2);
            }
            
            return {
              toolResult: {
                content: [{
                  type: 'text',
                  text: output
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
  
  private calculateSimilarity(str1: string, str2: string): number {
    // Simple Jaccard similarity based on words
    const words1 = new Set(str1.split(/\s+/));
    const words2 = new Set(str2.split(/\s+/));
    
    const intersection = new Set([...words1].filter(x => words2.has(x)));
    const union = new Set([...words1, ...words2]);
    
    return intersection.size / union.size;
  }
  
  async start() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('PrevostGo Inventory MCP Server started');
  }
}

// Start the server
const server = new PrevostGoInventoryServer();
server.start().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});
