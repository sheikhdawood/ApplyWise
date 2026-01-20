from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, List, Optional
from datetime import datetime
from jobQualityFilter import job_quality_filter_node
from AIMLmatching import aiml_matching_node
from applicationStrategy import application_strategy_node
from resumePositioning import resume_positioning_node
from coverLetter import cover_letter_node
from apply import apply_node
from trustUpdate import trust_update_node
from archive import archive_node
from jobDiscovery import job_discovery_node
from resumeIntelligence import resume_intelligence_node
from hold import hold_node

class AgentState(TypedDict, total=False):

    # Candidate
    candidate_profile: Dict[str, Any]
    resume_artifact: Dict[str, Any]

    # Job
    job_posting: Dict[str, Any]
    job_quality: Dict[str, Any]
    job_match: Dict[str, Any]

    # Decision
    application_decision: Dict[str, Any]

    # Assets
    resume_variant: Optional[Dict[str, Any]]
    cover_letter: Optional[Dict[str, Any]]

    # Execution
    application_result: Optional[Dict[str, Any]]

    # Trust
    platform_trust: Dict[str, Any]
    kill_switch: bool
    resume_path: str

    # Meta
    errors: List[str]
    timestamps: Dict[str, datetime]

def route_by_decision(state: AgentState) -> str:
    return state["application_decision"]["action"]

def kill_switch_guard(state: AgentState) -> str:
    if state.get("kill_switch", False):
        return "ABORT"
    return "CONTINUE"

graph = StateGraph(AgentState)

graph.add_node("resume_intelligence", resume_intelligence_node)
graph.add_node("job_discovery", job_discovery_node)
graph.add_node("job_quality_filter", job_quality_filter_node)
graph.add_node("aiml_matching", aiml_matching_node)
graph.add_node("application_strategy", application_strategy_node)

graph.add_node("resume_positioning", resume_positioning_node)
graph.add_node("cover_letter", cover_letter_node)
graph.add_node("apply", apply_node)
graph.add_node("trust_update", trust_update_node)

graph.add_node("hold", hold_node)
graph.add_node("archive", archive_node)

graph.set_entry_point("resume_intelligence")

graph.add_edge("resume_intelligence", "job_discovery")
graph.add_edge("job_discovery", "job_quality_filter")
graph.add_edge("job_quality_filter", "aiml_matching")
graph.add_edge("aiml_matching", "application_strategy")

graph.add_conditional_edges(
    "application_strategy",
    route_by_decision,
    {
        "APPLY": "resume_positioning",
        "HOLD": "hold",
        "SKIP": "archive",
    }
)
graph.add_edge("resume_positioning", "cover_letter")
graph.add_conditional_edges(
    "cover_letter",
    kill_switch_guard,
    {
        "CONTINUE": "apply",
        "ABORT": "archive",
    }
)
graph.add_conditional_edges(
    "apply",
    kill_switch_guard,
    {
        "CONTINUE": "trust_update",
        "ABORT": "archive",
    }
)
graph.add_edge("trust_update", END)
graph.add_edge("hold", END)
graph.add_edge("archive", END)
application_graph = graph.compile()
