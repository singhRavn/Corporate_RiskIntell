# Corporate Ownership & Risk Intelligence Platform

This project implements an MCP server natively harnessing the official `fastmcp` and `prefab-ui` frameworks to ingest, process, persist, and render corporate structure and risk data perfectly integrated into standard LLM hosts.

## System Architecture

**MCP Server (`mcp_server.py`)**: Defined using `fastmcp`, exposing four primary tools to the host:
- `fetch_corporate_data(query)`: Retrieves simulated structure perfectly formatted for AI processing.
- `file_crud(action, data)`: Translates state directly into local file storage securely.
- `render_prefab_ui(data)`: A standalone layout generator explicitly adopting `prefab-ui` components (e.g. `BarChart`, `Grid`, `Card`).
- **`run_corporate_analysis(query)`**: The complete end-to-end encapsulated **Agent Orchestration Logic**. Calling this tool automatically performs data-fetch, runs risk extraction, invokes `file_crud` to cache to disk, and natively returns the combined analytical state leveraging `@mcp.tool(app=True)` to stream the Interactive UI seamlessly into the UI-aware conversational host.

## Usage

You must ensure that the core libraries are installed:
```bash
pip install fastmcp prefab-ui
```

Launch the FastMCP UI Inspector or use it directly within your LLM gateway:
```bash
# Activate your python virtual environment if you used one:
source venv/bin/activate

# Using FastMCP CLI to test applications locally:
# (Specifying both ports to avoid any system conflicts)
fastmcp dev apps mcp_server.py --mcp-port 8023 --dev-port 8081

# Alternatively, just execute standard stdio testing:

## Documentation & Demo

### Video Demonstration
You can view or download the full end-to-end demonstration of the platform here:
[**Download Ownership_RiskIntell.mov (via GitHub)**](https://github.com/singhRavn/Corporate_RiskIntell/blob/main/Ownership_RiskIntell.mov)

This video walks through:
- **Agentic Pipeline**: Fetch ➔ AI Analysis ➔ Local Persistence.
- **MCP Integration**: How `fastmcp` tools are orchestrated over stdio.
- **Dynamic UI**: Detailed look at the D3 Physics Graph and Prefab dashboards.
```
