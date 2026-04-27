import os
import json
import subprocess
import threading
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='frontend')
CORS(app)

# Use the venv python to run the MCP server
PYTHON_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python")
if not os.path.exists(PYTHON_BIN):
    PYTHON_BIN = "python3"

MCP_SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")

class MCPClient:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        print(f"Launching MCP Server: {MCP_SERVER_PATH}")
        self.stderr_log = open("mcp_stderr.log", "w")
        self.process = subprocess.Popen(
            [PYTHON_BIN, MCP_SERVER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self.stderr_log,
            text=True,
            bufsize=1
        )
        self.msg_id = 1
        self._init_server()

    def _init_server(self):
        init_req = {
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "DedicatedAgent", "version": "1.0.0"}
            }
        }
        self._send(init_req)
        resp = self._recv()
        print(f"Server Initialized: {resp.get('result', {}).get('serverInfo', {}).get('name') if resp else 'FAILED'}")
        self.msg_id += 1

    def _send(self, data):
        self.process.stdin.write(json.dumps(data) + "\n")
        self.process.stdin.flush()

    def _recv(self):
        while True:
            line = self.process.stdout.readline()
            if not line: return None
            line = line.strip()
            if not line.startswith('{'):
                continue
            try:
                data = json.loads(line)
                if "method" in data and "id" not in data:
                    continue
                return data
            except json.JSONDecodeError:
                continue

    def call_tool(self, tool_name, arguments):
        req = {
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        self._send(req)
        resp = self._recv()
        self.msg_id += 1
        
        if resp and "result" in resp:
            result = resp["result"]
            # FastMCP usually provides structuredContent for tools returning objects
            if "structuredContent" in result:
                return result["structuredContent"]
            
            # Fallback to content list
            content = result.get("content", [])
            if content and content[0].get("type") == "text":
                text = content[0]["text"]
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text # Return raw text if not JSON
        return {"status": "error", "message": "Tool execution failed"}

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.json
        query = data.get("query", "")
        
        client = MCPClient.get_instance()
        
        # Call the unified agent pipeline tool
        ui_result = client.call_tool("run_corporate_analysis", {"query": query})
        
        return jsonify({
            "status": "success",
            "ui_schema": ui_result 
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    app.run(port=8023, debug=False) # Turned off debug to avoid double-init of MCP client
