#!/usr/bin/env python
"""
Script to run the Script2Video MCP server.

Usage:
    python run_mcp_server.py              # Run with streamable HTTP on localhost:8000
    python run_mcp_server.py stdio        # Run with stdio transport
"""
import sys
from src.script2video.mcp_server import mcp

if __name__ == "__main__":
    mcp.run()
