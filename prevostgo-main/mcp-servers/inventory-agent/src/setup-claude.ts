#!/usr/bin/env node

import { promises as fs } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const CLAUDE_CONFIG_PATH = join(homedir(), 'AppData', 'Roaming', 'Claude', 'claude_desktop_config.json');

interface ClaudeConfig {
  mcpServers: {
    [key: string]: {
      command: string;
      args: string[];
      env?: Record<string, string>;
    };
  };
}

async function setupClaudeConfig() {
  try {
    // Read existing config or create new one
    let config: ClaudeConfig = { mcpServers: {} };
    
    try {
      const existingConfig = await fs.readFile(CLAUDE_CONFIG_PATH, 'utf8');
      config = JSON.parse(existingConfig);
    } catch (error) {
      console.log('No existing Claude config found, creating new one...');
    }
    
    // Add our MCP server configuration
    const projectPath = process.cwd();
    config.mcpServers = config.mcpServers || {};
    config.mcpServers['prevostgo-inventory'] = {
      command: 'node',
      args: [join(projectPath, 'dist', 'index.js')],
      env: {
        API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
        PYTHON_EXECUTABLE: process.env.PYTHON_EXECUTABLE || 'python',
        SCRAPER_PATH: process.env.SCRAPER_PATH || 'C:\\Users\\tmcha\\Dev\\prevostgo\\backend\\scraper_final_v2.py'
      }
    };
    
    // Write the config
    await fs.mkdir(join(homedir(), 'AppData', 'Roaming', 'Claude'), { recursive: true });
    await fs.writeFile(CLAUDE_CONFIG_PATH, JSON.stringify(config, null, 2));
    
    console.log('✅ Claude Desktop configuration updated successfully!');
    console.log(`📁 Config location: ${CLAUDE_CONFIG_PATH}`);
    console.log('\n📋 Added MCP server: prevostgo-inventory');
    console.log('\nPlease restart Claude Desktop for changes to take effect.');
    
  } catch (error) {
    console.error('❌ Failed to setup Claude config:', error);
    console.log('\nManual setup instructions:');
    console.log('1. Open:', CLAUDE_CONFIG_PATH);
    console.log('2. Add the following to mcpServers:');
    console.log(JSON.stringify({
      'prevostgo-inventory': {
        command: 'node',
        args: [join(process.cwd(), 'dist', 'index.js')],
        env: {
          API_BASE_URL: 'http://localhost:8000',
          PYTHON_EXECUTABLE: 'python',
          SCRAPER_PATH: 'C:\\Users\\tmcha\\Dev\\prevostgo\\backend\\scraper_final_v2.py'
        }
      }
    }, null, 2));
  }
}

setupClaudeConfig();
