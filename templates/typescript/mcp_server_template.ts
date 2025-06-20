// TypeScript MCP Server Template
// Based on patterns from MCP Development Tools Server

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs/promises';

const execAsync = promisify(exec);

interface ToolConfig {
  name: string;
  description: string;
  inputSchema: any;
  handler: (args: any) => Promise<any>;
}

class {{ServerName}}Server {
  private server: Server;
  private tools: Map<string, ToolConfig> = new Map();

  // Security configuration - pattern from Dev Tools server
  private readonly ALLOWED_COMMANDS = [
    'ls', 'cat', 'grep', 'find', 'git', 'docker', 'npm', 'node'
  ];
  private readonly COMMAND_TIMEOUT = 30000; // 30 seconds
  private readonly MAX_OUTPUT_SIZE = 1024 * 1024; // 1MB

  constructor() {
    this.server = new Server({
      name: '{{server_name}}',
      version: '1.0.0',
      capabilities: {
        tools: {},
      },
    });

    this.setupToolHandlers();
    this.registerTools();
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools: Tool[] = Array.from(this.tools.values()).map(tool => ({
        name: tool.name,
        description: tool.description,
        inputSchema: tool.inputSchema
      }));

      return { tools };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        const tool = this.tools.get(name);
        if (!tool) {
          throw new Error(`Tool '${name}' not found`);
        }

        const result = await tool.handler(args || {});
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
        };
      } catch (error) {
        return {
          isError: true,
          content: [{ 
            type: 'text', 
            text: `Error: ${error instanceof Error ? error.message : String(error)}` 
          }]
        };
      }
    });
  }

  private registerTool(config: ToolConfig) {
    this.tools.set(config.name, config);
  }

  private registerTools() {
    // Execute command tool - core pattern from Dev Tools server
    this.registerTool({
      name: 'execute_command',
      description: 'Execute a system command safely with timeout and validation',
      inputSchema: {
        type: 'object',
        properties: {
          command: { type: 'string', description: 'Command to execute' },
          args: { 
            type: 'array', 
            items: { type: 'string' },
            description: 'Command arguments' 
          },
          cwd: { type: 'string', description: 'Working directory' }
        },
        required: ['command']
      },
      handler: this.executeCommand.bind(this)
    });

    // File operations - pattern from Dev Tools server
    this.registerTool({
      name: 'read_file',
      description: 'Read contents of a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'File path to read' },
          encoding: { type: 'string', description: 'File encoding', default: 'utf8' }
        },
        required: ['path']
      },
      handler: this.readFile.bind(this)
    });

    this.registerTool({
      name: 'write_file',
      description: 'Write content to a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'File path to write' },
          content: { type: 'string', description: 'Content to write' },
          encoding: { type: 'string', description: 'File encoding', default: 'utf8' }
        },
        required: ['path', 'content']
      },
      handler: this.writeFile.bind(this)
    });

    this.registerTool({
      name: 'list_directory',
      description: 'List directory contents',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Directory path to list' },
          detailed: { type: 'boolean', description: 'Include detailed file info' }
        },
        required: ['path']
      },
      handler: this.listDirectory.bind(this)
    });

    // Git operations - specialized pattern from Dev Tools server
    this.registerTool({
      name: 'git_command',
      description: 'Execute Git operations',
      inputSchema: {
        type: 'object',
        properties: {
          subcommand: { type: 'string', description: 'Git subcommand' },
          args: { 
            type: 'array', 
            items: { type: 'string' },
            description: 'Git arguments' 
          },
          cwd: { type: 'string', description: 'Repository directory' }
        },
        required: ['subcommand']
      },
      handler: this.gitCommand.bind(this)
    });

    // Docker operations - specialized pattern from Dev Tools server  
    this.registerTool({
      name: 'docker_command',
      description: 'Execute Docker operations',
      inputSchema: {
        type: 'object',
        properties: {
          subcommand: { type: 'string', description: 'Docker subcommand' },
          args: { 
            type: 'array', 
            items: { type: 'string' },
            description: 'Docker arguments' 
          },
          cwd: { type: 'string', description: 'Working directory' }
        },
        required: ['subcommand']
      },
      handler: this.dockerCommand.bind(this)
    });
  }

  private validateCommand(command: string): void {
    if (!this.ALLOWED_COMMANDS.includes(command)) {
      throw new Error(`Command '${command}' not allowed. Allowed commands: ${this.ALLOWED_COMMANDS.join(', ')}`);
    }
  }

  private sanitizeArgs(args: string[]): string[] {
    // Basic argument sanitization - pattern from Dev Tools server
    const dangerousPatterns = [';', '&', '|', '`', '$', '>', '<'];
    
    return args.map(arg => {
      if (dangerousPatterns.some(pattern => arg.includes(pattern))) {
        throw new Error(`Dangerous pattern in argument: ${arg}`);
      }
      return arg;
    });
  }

  private async executeCommand(params: any): Promise<any> {
    const { command, args = [], cwd } = params;
    
    // Validate and sanitize
    this.validateCommand(command);
    const sanitizedArgs = this.sanitizeArgs(args);
    
    const fullCommand = [command, ...sanitizedArgs].join(' ');
    
    try {
      const { stdout, stderr } = await execAsync(fullCommand, {
        timeout: this.COMMAND_TIMEOUT,
        cwd: cwd || process.cwd(),
        maxBuffer: this.MAX_OUTPUT_SIZE
      });

      return {
        stdout: stdout.toString(),
        stderr: stderr.toString(),
        command: fullCommand,
        success: true
      };
    } catch (error: any) {
      throw new Error(`Command failed: ${error.message}`);
    }
  }

  private async readFile(params: any): Promise<any> {
    const { path: filePath, encoding = 'utf8' } = params;
    
    try {
      const content = await fs.readFile(filePath, { encoding });
      const stats = await fs.stat(filePath);
      
      return {
        content,
        path: filePath,
        size: stats.size,
        modified: stats.mtime
      };
    } catch (error: any) {
      throw new Error(`Failed to read file: ${error.message}`);
    }
  }

  private async writeFile(params: any): Promise<any> {
    const { path: filePath, content, encoding = 'utf8' } = params;
    
    try {
      await fs.writeFile(filePath, content, { encoding });
      const stats = await fs.stat(filePath);
      
      return {
        path: filePath,
        size: stats.size,
        success: true
      };
    } catch (error: any) {
      throw new Error(`Failed to write file: ${error.message}`);
    }
  }

  private async listDirectory(params: any): Promise<any> {
    const { path: dirPath, detailed = false } = params;
    
    try {
      const entries = await fs.readdir(dirPath);
      
      if (!detailed) {
        return { entries, path: dirPath };
      }
      
      const detailedEntries = await Promise.all(
        entries.map(async (entry) => {
          const entryPath = path.join(dirPath, entry);
          const stats = await fs.stat(entryPath);
          
          return {
            name: entry,
            type: stats.isDirectory() ? 'directory' : 'file',
            size: stats.size,
            modified: stats.mtime
          };
        })
      );
      
      return { entries: detailedEntries, path: dirPath };
    } catch (error: any) {
      throw new Error(`Failed to list directory: ${error.message}`);
    }
  }

  private async gitCommand(params: any): Promise<any> {
    const { subcommand, args = [], cwd } = params;
    return this.executeCommand({
      command: 'git',
      args: [subcommand, ...args],
      cwd
    });
  }

  private async dockerCommand(params: any): Promise<any> {
    const { subcommand, args = [], cwd } = params;
    return this.executeCommand({
      command: 'docker',
      args: [subcommand, ...args],
      cwd
    });
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.run(transport);
  }
}

async function main() {
  const server = new {{ServerName}}Server();
  await server.run();
}

if (require.main === module) {
  main().catch(console.error);
}
