import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Row, Grid, Card, CardContent, Heading, Text, Badge, Separator
from prefab_ui.components.charts import BarChart, ChartSeries

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in environment. AI tools will fail.")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

mcp = FastMCP("CorporateIntelligencePlatform")

@mcp.tool()
def fetch_corporate_data(query: str) -> dict:
    """Fetch structured corporate data including ownership, subsidiaries, and risks."""
    query_lower = query.lower()
    data = {"company": "Reliance Industries Limited", "ticker": "RELIANCE.NS"}
    
    if "reliance" in query_lower:
        data["subsidiaries"] = [
            {"name": "Jio Platforms Limited", "ownership_pct": 67.03, "sector": "Telecom & Digital"},
            {"name": "Reliance Retail Ventures", "ownership_pct": 85.06, "sector": "Retail"},
            {"name": "Network18 Media", "ownership_pct": 73.15, "sector": "Media"},
            {"name": "Reliance New Energy", "ownership_pct": 100.0, "sector": "Green Energy"}
        ]
        data["risks"] = [
            {"type": "Regulatory", "severity": "Medium", "description": "Ongoing scrutiny over telecom pricing regulations."},
            {"type": "Debt", "severity": "Low", "description": "High capital expenditure in 5G, well-balanced by cash reserves."},
            {"type": "Legal", "severity": "Low", "description": "Routine legal challenges in subsidiary operations."}
        ]
        data["shareholding"] = {"Promoters": 50.39, "FII": 22.55, "DII": 16.34, "Public": 10.72}
    else:
        data["company"] = query
        data["subsidiaries"] = []
        data["risks"] = []

    return {"status": "success", "fetched_data": data}

@mcp.tool()
def file_crud(action: str, data: dict) -> dict:
    """Perform LOCAL file operations to store ownership structure and risk flags."""
    filename = data.get("filename", "default.json")
    filepath = os.path.join(DATA_DIR, filename)
    
    if action == "create" or action == "update":
        content = data.get("content", {})
        content["_updated_at"] = datetime.now().isoformat()
        with open(filepath, "w") as f:
            json.dump(content, f, indent=2)
        return {"status": "success", "message": f"File {filename} written.", "path": filepath}
    
    elif action == "read":
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return {"status": "success", "content": json.load(f)}
        return {"status": "error", "message": "File not found"}
            
    elif action == "delete":
        if os.path.exists(filepath):
            os.remove(filepath)
            return {"status": "success", "message": f"File {filename} deleted."}
        return {"status": "error", "message": "File not found"}
    
    return {"status": "error", "message": "Invalid action"}

@mcp.tool()
def generate_ai_report(corporate_data: dict) -> dict:
    """Use Gemini Flash to perform deep risk analysis and generate an executive report."""
    if not GEMINI_API_KEY:
        return {
            "status": "error",
            "message": "GEMINI_API_KEY missing. Please configure it in your .env file."
        }
    
    try:
        model = genai.GenerativeModel("gemini-3-flash-preview")
        
        prompt = f"""
        Analyze the following corporate data and generate a professional executive intelligence report.
        Focus on:
        1. Ownership structure complexity.
        2. Potential risk vulnerabilities (regulatory, financial, legal).
        3. Strategic recommendations.
        
        Data:
        {json.dumps(corporate_data, indent=2)}
        
        Return the report in the following JSON format:
        {{
            "summary": "A concise executive summary",
            "detailed_analysis": "In-depth breakdown of risks and structure",
            "risk_score": "Scale 1-10",
            "recommendations": ["List", "of", "actions"]
        }}
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        
        return {
            "status": "success",
            "report": json.loads(response.text)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool(app=True)
def render_prefab_ui(data: dict, ai_report: dict = None) -> ToolResult:
    """Generate interactive UI schema using Prefab UI."""
    company = data.get("company", "Unknown")
    subsidiaries = data.get("subsidiaries", [])
    risks = data.get("risks", [])
    shareholding = data.get("shareholding", {})

    with Column(gap=6, css_class="p-8") as view:
        Heading(f"Intelligence Report: {company}")
        Separator()
        
        with Grid(columns=2, gap=6):
            # Main Content Area - Ownership Graph and Structure
            with Card():
                with CardContent():
                    Text("Subsidiary Structure", css_class="font-semibold text-lg mb-4")
                    
                    # Generate nodes and links for D3 ForceGraph
                    nodes = [{"id": company, "label": company, "type": "parent"}]
                    edges = [{"source": company, "target": sub["name"]} for sub in subsidiaries]
                    for sub in subsidiaries:
                        nodes.append({"id": sub["name"], "label": f"{sub['name']} ({sub['ownership_pct']}%)", "type": "subsidiary"})
                    
                    graph_data = json.dumps({"nodes": nodes, "links": edges})
                    
                    with Column(css_class="force-graph-container"):
                        Text(graph_data, css_class="hidden")
            
            # Sidebar / Risk Area
            with Card(css_class="h-full"):
                with CardContent():
                    Text("Risk Indicators", css_class="font-semibold text-lg text-white mb-4")
                    with Column(gap=4):
                        for risk in risks:
                            variant = "destructive" if risk['severity'] == "High" else "warning" if risk['severity'] == "Medium" else "success"
                            with Card(css_class="bg-black/20 border-white/5 shadow-none"):
                                with CardContent():
                                    with Row():
                                        Text(risk['type'], css_class="font-bold flex-1 text-white")
                                        Badge(risk['severity'], variant=variant)
                                    Text(risk['description'], css_class="text-sm text-gray-400 mt-2")

        # Executive Conclusion (AI Enhanced if available)
        with Card(css_class="bg-blue-900/10 border-l-4 border-l-blue-500 mt-6"):
            with CardContent():
                title = "AI Executive Intelligence" if ai_report else "Executive Conclusion"
                Text(title, css_class="font-bold text-lg text-blue-400 mb-2")
                
                if ai_report:
                    summary_text = ai_report.get("summary", "No summary generated.")
                    Text(summary_text, css_class="text-slate-300 leading-relaxed")
                    
                    with Column(gap=2, css_class="mt-4"):
                        Text("Strategic Recommendations:", css_class="text-sm font-semibold text-white/70")
                        for rec in ai_report.get("recommendations", []):
                            Text(f"• {rec}", css_class="text-sm text-slate-400 ml-2")
                    
                    with Row(css_class="mt-4 items-center gap-2"):
                        Text("Risk Score:", css_class="text-sm font-semibold")
                        Badge(str(ai_report.get("risk_score", "N/A")), variant="destructive" if int(ai_report.get("risk_score", 0)) > 6 else "warning")
                else:
                    summary_text = (
                        f"{company} demonstrates a balanced risk profile with {len(subsidiaries)} core subsidiaries. "
                        "Primary vulnerabilities center around regulatory scrutiny and capital expenditure, "
                        "though strong systemic backing offsets immediate liabilities. Operations remain highly secure."
                    )
                    Text(summary_text, css_class="text-slate-300 leading-relaxed")

        Separator()
        
        # ... rest of the references ...
        with Column(gap=4):
            Text("Reference Document Grounding", css_class="font-semibold text-lg text-white mb-2")
            with Grid(columns=3, gap=6):
                # (Keep existing cards)
                with Card(css_class="bg-blue-500/5 hover:bg-blue-500/10 cursor-pointer border-blue-500/20"):
                    with CardContent():
                        Text("SEBI Compliance Docs", weight="bold", css_class="text-blue-400")
                        Text("Last accessed: 24h ago", size="sm", color="muted")
                with Card(css_class="bg-emerald-500/5 hover:bg-emerald-500/10 cursor-pointer border-emerald-500/20"):
                    with CardContent():
                        Text("Ministry of Corporate Affairs", weight="bold", css_class="text-emerald-400")
                        Text("Annual Returns (MGT-7)", size="sm", color="muted")
                with Card(css_class="bg-purple-500/5 hover:bg-purple-500/10 cursor-pointer border-purple-500/20"):
                    with CardContent():
                        Text("Global Legal Entity Identifier", weight="bold", css_class="text-purple-400")
                        Text("LEI: 335800QW1OMNXXK0A261", size="sm", color="muted")

    # Generate the ToolResult which gives LLM context and renders the view!
    llm_context = f"Company: {company}. Found {len(subsidiaries)} subsidiaries and {len(risks)} risk flags."
    if ai_report:
        llm_context += f" AI Risk Score: {ai_report.get('risk_score')}."
        
    return ToolResult(
        content=llm_context,
        structured_content=view
    )

@mcp.tool(app=True)
def run_corporate_analysis(query: str) -> ToolResult:
    """Agent pipeline: Fetches data, runs Gemini analysis, extracts risks, saves to disk, and renders the UI."""
    # Step 1: Fetch
    fetch_resp = fetch_corporate_data(query)
    corporate_data = fetch_resp["fetched_data"]
    
    # Step 2: Gemini Analysis
    ai_report_resp = generate_ai_report(corporate_data)
    ai_report = ai_report_resp.get("report") if ai_report_resp["status"] == "success" else None
    
    # Step 3: Save logically via file_crud (Include AI report in saved data)
    company_slug = "".join([c if c.isalnum() else "_" for c in corporate_data.get("company", query).lower()])
    file_crud("create", {
        "filename": f"{company_slug}.json",
        "content": {
            "data": corporate_data,
            "ai_analysis": ai_report
        }
    })
    
    # Step 4: Render UI via Prefab
    return render_prefab_ui(corporate_data, ai_report=ai_report)

if __name__ == "__main__":
    mcp.run()
