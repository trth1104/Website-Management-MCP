#!/usr/bin/env python3
"""
MCP Server for Full Stack Website & Database Management
Provides tools for managing databases and full stack web development
"""

import asyncio
import json
import os
import mysql.connector
from typing import Any, Optional
from pathlib import Path
import re
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "aperire_local")
}

# Workspace root from environment variable
WORKSPACE_ROOT = Path(os.getenv("WORKSPACE_ROOT", r"c:\xampp\htdocs\testweb"))

# Initialize MCP server
app = Server("web-management-mcp")


# =============================================================================
# DATABASE MANAGEMENT TOOLS
# =============================================================================

def get_db_connection():
    """Create and return database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        raise Exception(f"Database connection error: {err}")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        # Database Management Tools
        Tool(
            name="db_query",
            description="Execute SELECT query on database and return results",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "params": {
                        "type": "array",
                        "description": "Parameters for prepared statement (optional)",
                        "items": {"type": "string"}
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="db_execute",
            description="Execute INSERT, UPDATE, DELETE queries on database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute (INSERT, UPDATE, DELETE)"
                    },
                    "params": {
                        "type": "array",
                        "description": "Parameters for prepared statement (optional)",
                        "items": {"type": "string"}
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="db_get_tables",
            description="List all tables in the database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="db_get_table_schema",
            description="Get schema/structure of a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="db_get_table_data",
            description="Get all data from a specific table with optional limit",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of rows to return (default: 100)"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="db_backup_table",
            description="Generate SQL backup for a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to backup"
                    }
                },
                "required": ["table_name"]
            }
        ),
        
        # File Management Tools
        Tool(
            name="file_read",
            description="Read content of a file in the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to the file from workspace root"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="file_write",
            description="Write or update content of a file in the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to the file from workspace root"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="file_list",
            description="List files and directories in a path",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Relative path from workspace root (use '.' for root)"
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="file_search",
            description="Search for files containing specific text or pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Text or regex pattern to search for"
                    },
                    "file_extension": {
                        "type": "string",
                        "description": "Filter by file extension (e.g., 'php', 'html', 'css')"
                    }
                },
                "required": ["pattern"]
            }
        ),
        
        # Web Stack Analysis Tools
        Tool(
            name="analyze_project_structure",
            description="Analyze the complete project structure and dependencies",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="analyze_php_files",
            description="Analyze all PHP files for functions, classes, and dependencies",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="analyze_dependencies",
            description="Analyze file dependencies and relationships in the project",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="generate_api_docs",
            description="Generate API documentation for PHP endpoints",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="check_security",
            description="Perform basic security checks on PHP files",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution"""
    
    try:
        # Database Tools
        if name == "db_query":
            result = await db_query(arguments.get("query"), arguments.get("params"))
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "db_execute":
            result = await db_execute(arguments.get("query"), arguments.get("params"))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "db_get_tables":
            result = await db_get_tables()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "db_get_table_schema":
            result = await db_get_table_schema(arguments.get("table_name"))
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "db_get_table_data":
            result = await db_get_table_data(
                arguments.get("table_name"),
                arguments.get("limit", 100)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "db_backup_table":
            result = await db_backup_table(arguments.get("table_name"))
            return [TextContent(type="text", text=result)]
        
        # File Tools
        elif name == "file_read":
            result = await file_read(arguments.get("file_path"))
            return [TextContent(type="text", text=result)]
        
        elif name == "file_write":
            result = await file_write(
                arguments.get("file_path"),
                arguments.get("content")
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "file_list":
            result = await file_list(arguments.get("directory"))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "file_search":
            result = await file_search(
                arguments.get("pattern"),
                arguments.get("file_extension")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # Analysis Tools
        elif name == "analyze_project_structure":
            result = await analyze_project_structure()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_php_files":
            result = await analyze_php_files()
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "analyze_dependencies":
            result = await analyze_dependencies()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "generate_api_docs":
            result = await generate_api_docs()
            return [TextContent(type="text", text=result)]
        
        elif name == "check_security":
            result = await check_security()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# =============================================================================
# DATABASE TOOL IMPLEMENTATIONS
# =============================================================================

async def db_query(query: str, params: Optional[list] = None) -> dict:
    """Execute SELECT query"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        
        return {
            "status": "success",
            "rows": len(results),
            "data": results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if conn:
            conn.close()


async def db_execute(query: str, params: Optional[list] = None) -> dict:
    """Execute INSERT, UPDATE, DELETE queries"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        
        return {
            "status": "success",
            "affected_rows": cursor.rowcount,
            "last_insert_id": cursor.lastrowid if cursor.lastrowid else None
        }
    except Exception as e:
        if conn:
            conn.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if conn:
            conn.close()


async def db_get_tables() -> dict:
    """Get list of all tables"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if conn:
            conn.close()


async def db_get_table_schema(table_name: str) -> dict:
    """Get table schema"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"DESCRIBE {table_name}")
        schema = cursor.fetchall()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        row_count = cursor.fetchone()['count']
        
        return {
            "status": "success",
            "table": table_name,
            "row_count": row_count,
            "schema": schema
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if conn:
            conn.close()


async def db_get_table_data(table_name: str, limit: int = 100) -> dict:
    """Get data from table"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        data = cursor.fetchall()
        
        return {
            "status": "success",
            "table": table_name,
            "rows": len(data),
            "data": data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if conn:
            conn.close()


async def db_backup_table(table_name: str) -> str:
    """Generate SQL backup for table"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get table structure
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        create_table = cursor.fetchone()[f'Create Table']
        
        # Get data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Generate SQL
        sql = f"-- Backup for table: {table_name}\n"
        sql += f"-- Generated: {asyncio.get_event_loop().time()}\n\n"
        sql += f"DROP TABLE IF EXISTS `{table_name}`;\n\n"
        sql += f"{create_table};\n\n"
        
        if rows:
            # Get column names
            columns = list(rows[0].keys())
            sql += f"INSERT INTO `{table_name}` (`{'`, `'.join(columns)}`) VALUES\n"
            
            values = []
            for row in rows:
                row_values = []
                for col in columns:
                    val = row[col]
                    if val is None:
                        row_values.append("NULL")
                    elif isinstance(val, str):
                        row_values.append(f"'{val.replace(chr(39), chr(39) + chr(39))}'")
                    else:
                        row_values.append(str(val))
                values.append(f"({', '.join(row_values)})")
            
            sql += ',\n'.join(values) + ';\n'
        
        return sql
        
    except Exception as e:
        return f"-- Error: {str(e)}"
    finally:
        if conn:
            conn.close()


# =============================================================================
# FILE MANAGEMENT IMPLEMENTATIONS
# =============================================================================

async def file_read(file_path: str) -> str:
    """Read file content"""
    try:
        full_path = WORKSPACE_ROOT / file_path
        if not full_path.exists():
            return f"Error: File not found: {file_path}"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


async def file_write(file_path: str, content: str) -> str:
    """Write to file"""
    try:
        full_path = WORKSPACE_ROOT / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


async def file_list(directory: str) -> dict:
    """List files in directory"""
    try:
        full_path = WORKSPACE_ROOT / directory
        if not full_path.exists():
            return {"error": f"Directory not found: {directory}"}
        
        items = {
            "directories": [],
            "files": []
        }
        
        for item in full_path.iterdir():
            if item.is_dir():
                items["directories"].append(item.name)
            else:
                items["files"].append({
                    "name": item.name,
                    "size": item.stat().st_size,
                    "extension": item.suffix
                })
        
        return items
    except Exception as e:
        return {"error": str(e)}


async def file_search(pattern: str, file_extension: Optional[str] = None) -> dict:
    """Search for pattern in files"""
    try:
        results = []
        
        for file_path in WORKSPACE_ROOT.rglob('*'):
            if file_path.is_file():
                # Filter by extension if provided
                if file_extension and not file_path.suffix.endswith(file_extension):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if re.search(pattern, content, re.IGNORECASE):
                            # Find all matches with line numbers
                            matches = []
                            for i, line in enumerate(content.split('\n'), 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    matches.append({
                                        "line": i,
                                        "content": line.strip()[:100]  # Limit line length
                                    })
                            
                            results.append({
                                "file": str(file_path.relative_to(WORKSPACE_ROOT)),
                                "matches": len(matches),
                                "lines": matches[:10]  # Limit to first 10 matches
                            })
                except:
                    continue
        
        return {
            "pattern": pattern,
            "files_found": len(results),
            "results": results
        }
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# WEB STACK ANALYSIS IMPLEMENTATIONS
# =============================================================================

async def analyze_project_structure() -> dict:
    """Analyze complete project structure"""
    try:
        structure = {
            "frontend": {"html": [], "css": [], "js": []},
            "backend": {"php": []},
            "database": {"sql": []},
            "assets": {"images": [], "videos": [], "fonts": [], "other": []},
            "config": [],
            "documentation": []
        }
        
        for file_path in WORKSPACE_ROOT.rglob('*'):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(WORKSPACE_ROOT))
                ext = file_path.suffix.lower()
                
                if ext == '.html':
                    structure["frontend"]["html"].append(rel_path)
                elif ext == '.css':
                    structure["frontend"]["css"].append(rel_path)
                elif ext in ['.js', '.jsx']:
                    structure["frontend"]["js"].append(rel_path)
                elif ext == '.php':
                    structure["backend"]["php"].append(rel_path)
                elif ext == '.sql':
                    structure["database"]["sql"].append(rel_path)
                elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']:
                    structure["assets"]["images"].append(rel_path)
                elif ext in ['.mp4', '.webm', '.ogg']:
                    structure["assets"]["videos"].append(rel_path)
                elif ext in ['.ttf', '.woff', '.woff2', '.eot']:
                    structure["assets"]["fonts"].append(rel_path)
                elif ext in ['.json', '.xml', '.ini', '.env']:
                    structure["config"].append(rel_path)
                elif ext in ['.md', '.txt', '.pdf']:
                    structure["documentation"].append(rel_path)
        
        # Count totals
        structure["summary"] = {
            "total_html_files": len(structure["frontend"]["html"]),
            "total_css_files": len(structure["frontend"]["css"]),
            "total_js_files": len(structure["frontend"]["js"]),
            "total_php_files": len(structure["backend"]["php"]),
            "total_sql_files": len(structure["database"]["sql"])
        }
        
        return structure
    except Exception as e:
        return {"error": str(e)}


async def analyze_php_files() -> dict:
    """Analyze PHP files for functions and classes"""
    try:
        php_analysis = {}
        
        for file_path in WORKSPACE_ROOT.rglob('*.php'):
            rel_path = str(file_path.relative_to(WORKSPACE_ROOT))
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find functions
            functions = re.findall(r'function\s+(\w+)\s*\(', content)
            
            # Find classes
            classes = re.findall(r'class\s+(\w+)', content)
            
            # Find includes/requires
            includes = re.findall(r'(?:include|require)(?:_once)?\s*[(\']([^)\']+)', content)
            
            # Find database queries
            db_queries = len(re.findall(r'\$conn->|mysqli_|mysql_', content))
            
            php_analysis[rel_path] = {
                "functions": functions,
                "classes": classes,
                "includes": includes,
                "db_operations": db_queries,
                "lines_of_code": len(content.split('\n'))
            }
        
        return php_analysis
    except Exception as e:
        return {"error": str(e)}


async def analyze_dependencies() -> dict:
    """Analyze file dependencies"""
    try:
        dependencies = {}
        
        for file_path in WORKSPACE_ROOT.rglob('*.php'):
            rel_path = str(file_path.relative_to(WORKSPACE_ROOT))
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find includes/requires
            includes = re.findall(r'(?:include|require)(?:_once)?\s*[(\']([^)\'";]+)', content)
            
            dependencies[rel_path] = [inc.strip() for inc in includes]
        
        return dependencies
    except Exception as e:
        return {"error": str(e)}


async def generate_api_docs() -> str:
    """Generate API documentation for PHP endpoints"""
    try:
        docs = "# API Documentation\n\n"
        
        for file_path in WORKSPACE_ROOT.rglob('*.php'):
            rel_path = str(file_path.relative_to(WORKSPACE_ROOT))
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find functions with comments
            function_pattern = r'/\*\*(.*?)\*/\s*function\s+(\w+)\s*\((.*?)\)'
            matches = re.findall(function_pattern, content, re.DOTALL)
            
            if matches:
                docs += f"## {rel_path}\n\n"
                for comment, func_name, params in matches:
                    docs += f"### `{func_name}({params})`\n\n"
                    docs += f"{comment.strip()}\n\n"
        
        return docs
    except Exception as e:
        return f"Error: {str(e)}"


async def check_security() -> dict:
    """Perform basic security checks"""
    try:
        issues = []
        
        security_patterns = [
            (r'\$_(?:GET|POST|REQUEST)\[(?!.*(?:mysqli_real_escape_string|htmlspecialchars|filter_input))', 
             'Potential SQL injection or XSS vulnerability'),
            (r'eval\s*\(', 'Use of eval() - security risk'),
            (r'exec\s*\(|system\s*\(|shell_exec\s*\(', 'Command execution function'),
            (r'md5\s*\(.*password', 'Weak password hashing (MD5)'),
        ]
        
        for file_path in WORKSPACE_ROOT.rglob('*.php'):
            rel_path = str(file_path.relative_to(WORKSPACE_ROOT))
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern, description in security_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "file": rel_path,
                        "line": line_num,
                        "issue": description,
                        "code": match.group()[:50]
                    })
        
        return {
            "total_issues": len(issues),
            "issues": issues
        }
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# RESOURCES
# =============================================================================

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="config://database",
            name="Database Configuration",
            description="Current database configuration",
            mimeType="application/json"
        ),
        Resource(
            uri="config://workspace",
            name="Workspace Configuration",
            description="Current workspace path and settings",
            mimeType="application/json"
        )
    ]


@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "config://database":
        return json.dumps(DB_CONFIG, indent=2)
    elif uri == "config://workspace":
        return json.dumps({
            "workspace_root": str(WORKSPACE_ROOT),
            "exists": WORKSPACE_ROOT.exists()
        }, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="web-management-mcp",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
