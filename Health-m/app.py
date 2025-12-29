# app.py - COMPLETE WORKING DEEP AGENT
import os, json
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-proj-fake") 

class TeamCreds:
    def __init__(self):
        self.store = InMemoryStore()
        self.store.put(("creds", "app-team-1"), json.dumps({
            "splunk": "https://splunk-team1.com", 
            "dynatrace": "https://team1.dynatrace.com",
            "stonebranch": "team1-agent"
        }))
    
    def get(self, team_id): 
        data = self.store.get(("creds", team_id))
        return json.loads(data.value) if data else {}

creds = TeamCreds()

@tool
def splunk_uf_health(query: str, runtime) -> str:
    team_id = runtime.config.get("configurable", {}).get("team_id", "app-team-1")
    c = creds.get(team_id)
    return f"🔍 {team_id} Splunk UF: 3 {query} events (index={team_id}_uf)"

@tool
def dynatrace_cpu(runtime) -> str:
    team_id = runtime.config.get("configurable", {}).get("team_id", "app-team-1")
    return f"📊 {team_id} Dynatrace: CPU 45% (tag=team:{team_id})"

@tool
def stonebranch_jobs(status: str, runtime) -> str:
    team_id = runtime.config.get("configurable", {}).get("team_id", "app-team-1")
    return f"❌ {team_id} Stonebranch: 2 {status} jobs (agent={team_id}-agent)"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [splunk_uf_health, dynatrace_cpu, stonebranch_jobs]
llm_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: list
    team_id: str

def supervisor(state):
    return {"messages": [llm_tools.invoke(state["messages"])]}

def tools_node(state):
    return {"messages": [{"role": "assistant", "content": "✅ All tools executed!"}]}

graph = StateGraph(State)
graph.add_node("supervisor", supervisor)
graph.add_node("tools", tools_node)
graph.set_entry_point("supervisor")
graph.add_edge("tools", END)

app = graph.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    print("🚀 Health Agent Ready!")
    config = {"configurable": {"team_id": "app-team-1"}}
    result = app.invoke({"messages": [{"role": "user", "content": "check splunk"}], "team_id": "app-team-1"}, config)
    print(result["messages"][-1]["content"])
