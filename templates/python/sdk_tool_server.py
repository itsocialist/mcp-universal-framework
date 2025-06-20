# Traditional SDK Tool Server Template  
# Based on patterns from MCP Development Tools Server

import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from mcp_framework import SDKWrapper, ConfigLoader, ValidationError, TimeoutError, ToolError

# Load configuration
config = ConfigLoader()
config.load_env()

# Create server with traditional SDK pattern
server = SDKWrapper(
    name="{{tool_name}}-mcp-server",
    config=config
)

# Security configuration - pattern from Dev Tools server
ALLOWED_COMMANDS = config.get("allowed_commands", [
    "ls", "cat", "grep", "find", "git", "docker", "npm", "python"
])
COMMAND_TIMEOUT = config.get("command_timeout", 30)
MAX_OUTPUT_SIZE = config.get("max_output_size", 1024 * 1024)  # 1MB

class CommandValidator:
    """Command validation following security patterns from Dev Tools server"""
    
    @staticmethod
    def validate_command(command: str, args: List[str] = None) -> bool:
        """Validate command against whitelist"""
        if command not in ALLOWED_COMMANDS:
            raise ValidationError(
                f"Command '{command}' not allowed",
                parameter="command"
            )
        return True
    
    @staticmethod
    def sanitize_args(args: List[str]) -> List[str]:
        """Basic argument sanitization"""
        # Remove potentially dangerous arguments
        dangerous_patterns = [";", "&", "|", "`", "$", ">", "<"]
        
        sanitized = []
        for arg in args:
            if any(pattern in arg for pattern in dangerous_patterns):
                raise ValidationError(f"Dangerous pattern in argument: {arg}")
            sanitized.append(arg)
        
        return sanitized

@server.tool()
async def execute_command(command: str, args: List[str] = None, cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a system command safely
    
    Pattern extracted from Dev Tools server with security restrictions.
    
    Args:
        command: Command to execute
        args: Command arguments  
        cwd: Working directory
        
    Returns:
        dict: Command output and metadata
    """
    args = args or []
    
    # Validate command and arguments
    CommandValidator.validate_command(command, args)
    sanitized_args = CommandValidator.sanitize_args(args)
    
    # Build full command
    full_command = [command] + sanitized_args
    
    try:
        # Execute with timeout - common pattern from Dev Tools
        process = await asyncio.create_subprocess_exec(
            *full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=COMMAND_TIMEOUT
            )
        except asyncio.TimeoutError:
            process.kill()
            raise TimeoutError(
                f"Command timed out after {COMMAND_TIMEOUT} seconds",
                timeout_seconds=COMMAND_TIMEOUT
            )
        
        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')
        
        # Check output size limits
        if len(stdout_text) > MAX_OUTPUT_SIZE:
            stdout_text = stdout_text[:MAX_OUTPUT_SIZE] + "\n[Output truncated]"
        
        # Check for command failure
        if process.returncode != 0:
            raise ToolError(
                f"Command failed with exit code {process.returncode}",
                tool_name=command,
                exit_code=process.returncode,
                stderr=stderr_text
            )
        
        return {
            "stdout": stdout_text,
            "stderr": stderr_text,
            "exit_code": process.returncode,
            "command": " ".join(full_command)
        }
        
    except Exception as e:
        if isinstance(e, (ValidationError, TimeoutError, ToolError)):
            raise
        raise ToolError(f"Command execution failed: {str(e)}", tool_name=command)

@server.tool()
def list_allowed_commands() -> Dict[str, Any]:
    """
    List allowed commands
    
    Security feature from Dev Tools server.
    """
    return {
        "allowed_commands": ALLOWED_COMMANDS,
        "timeout": COMMAND_TIMEOUT,
        "max_output_size": MAX_OUTPUT_SIZE
    }

@server.tool()
async def git_command(subcommand: str, args: List[str] = None, cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Git operations
    
    Specialized tool pattern from Dev Tools server.
    
    Args:
        subcommand: Git subcommand (status, add, commit, etc.)
        args: Additional arguments
        cwd: Repository directory
        
    Returns:
        dict: Git command output
    """
    args = args or []
    git_args = [subcommand] + args
    
    return await execute_command("git", git_args, cwd)

@server.tool()
async def docker_command(subcommand: str, args: List[str] = None, cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Docker operations
    
    Specialized tool pattern from Dev Tools server.
    
    Args:
        subcommand: Docker subcommand (ps, build, run, etc.)
        args: Additional arguments
        cwd: Working directory
        
    Returns:
        dict: Docker command output
    """
    args = args or []
    docker_args = [subcommand] + args
    
    return await execute_command("docker", docker_args, cwd)

@server.tool()
def read_file(file_path: str, max_lines: int = 100) -> Dict[str, Any]:
    """
    Read file contents with size limits
    
    File operation pattern from Dev Tools server.
    
    Args:
        file_path: Path to file
        max_lines: Maximum lines to read
        
    Returns:
        dict: File contents and metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"[File truncated after {max_lines} lines]")
                    break
                lines.append(line.rstrip())
        
        return {
            "file_path": file_path,
            "lines": lines,
            "line_count": len(lines),
            "truncated": len(lines) >= max_lines
        }
        
    except FileNotFoundError:
        raise ValidationError(f"File not found: {file_path}", parameter="file_path")
    except PermissionError:
        raise ValidationError(f"Permission denied: {file_path}", parameter="file_path")
    except Exception as e:
        raise ToolError(f"Failed to read file: {str(e)}", tool_name="read_file")

@server.tool()
def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Write content to file
    
    File operation pattern from Dev Tools server.
    
    Args:
        file_path: Path to file
        content: Content to write
        
    Returns:
        dict: Write operation result
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "file_path": file_path,
            "bytes_written": len(content.encode('utf-8')),
            "success": True
        }
        
    except PermissionError:
        raise ValidationError(f"Permission denied: {file_path}", parameter="file_path")
    except Exception as e:
        raise ToolError(f"Failed to write file: {str(e)}", tool_name="write_file")

if __name__ == "__main__":
    # Run the server
    server.run()
