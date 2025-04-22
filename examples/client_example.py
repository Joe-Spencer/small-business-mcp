#!/usr/bin/env python3
"""
Example client for the Small Business MCP Server.

This script demonstrates how to:
1. Connect to the MCP server
2. List and use available tools
3. Access and render resources
4. Apply prompt templates
"""

import asyncio
import json
from typing import Dict, Any, List
from mcp import ClientSession, StdioServerParameters, types

async def print_separator(title: str):
    """Print a section separator with a title."""
    print("\n" + "=" * 40)
    print(f" {title}")
    print("=" * 40)

async def demo_tools(session: ClientSession):
    """Demonstrate tool discovery and usage."""
    await print_separator("TOOLS DEMONSTRATION")
    
    # List available tools
    tools = await session.list_tools()
    print(f"Available tools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")

    # Example: Query business data
    print("\nQuerying business data...")
    query_result = await session.call_tool(
        "query_business_data",
        arguments={"query": "Show me all PDF documents from 2023"}
    )
    print(f"Query result: {json.dumps(query_result, indent=2)}")

async def demo_resources(session: ClientSession):
    """Demonstrate resource discovery and access."""
    await print_separator("RESOURCES DEMONSTRATION")
    
    # List available resources
    resources = await session.list_resources()
    print(f"Available resources ({len(resources)}):")
    for resource in resources:
        print(f"  - {resource.name}: {resource.description}")

    # Example: Get database schema
    print("\nFetching database schema...")
    db_schema, mime_type = await session.read_resource("schema://database")
    print(f"Database schema (mime-type: {mime_type}):")
    try:
        # Try to parse as JSON
        schema_dict = json.loads(db_schema)
        print(json.dumps(schema_dict, indent=2))
    except:
        # Or print as string
        print(db_schema)

    # Example: Get business stats
    print("\nFetching business statistics...")
    stats, mime_type = await session.read_resource("stats://business")
    print(f"Business stats (mime-type: {mime_type}):")
    try:
        # Try to parse as JSON
        stats_dict = json.loads(stats)
        print(json.dumps(stats_dict, indent=2))
    except:
        # Or print as string
        print(stats)

async def demo_prompts(session: ClientSession):
    """Demonstrate prompt discovery and application."""
    await print_separator("PROMPTS DEMONSTRATION")
    
    # List available prompts
    prompts = await session.list_prompts()
    print(f"Available prompts ({len(prompts)}):")
    for prompt in prompts:
        print(f"  - {prompt.name}: {prompt.description}")
        if prompt.arguments:
            print("    Arguments:")
            for arg in prompt.arguments:
                print(f"      - {arg.name}: {arg.description} (required: {arg.required})")

    # Example: Get a report generation prompt
    print("\nGetting report generation prompt...")
    prompt_result = await session.get_prompt(
        "generate_report", 
        arguments={
            "report_type": "quarterly financial", 
            "time_period": "Q2 2023"
        }
    )
    
    print("Prompt messages:")
    for msg in prompt_result.messages:
        print(f"  [{msg.role}]: {msg.content.text}")

    # Example: Get a data analysis prompt
    print("\nGetting data analysis prompt...")
    prompt_result = await session.get_prompt(
        "analyze_data", 
        arguments={
            "data_type": "sales", 
            "analysis_focus": "seasonal patterns"
        }
    )
    
    print("Prompt messages:")
    for msg in prompt_result.messages:
        print(f"  [{msg.role}]: {msg.content.text}")

async def main():
    """Main function to run the MCP client examples."""
    # Create server parameters for connecting to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "MCPServer.server"],
        env=None,  # Optional environment variables
    )
    
    print("Connecting to Small Business MCP Server...")
    
    async with ClientSession(server_params) as session:
        # Initialize connection
        await session.initialize()
        print(f"Connected to MCP server: {session.server_name} v{session.server_version}")
        
        # Demonstrate tools
        await demo_tools(session)
        
        # Demonstrate resources
        await demo_resources(session)
        
        # Demonstrate prompts
        await demo_prompts(session)
        
        print("\nClient example completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 