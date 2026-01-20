from db.repositories import (
    has_application,
    is_archived,
    has_skip_decision,
    is_on_hold
)

def should_run_graph(job_id: str, candidate_id: str) -> tuple[bool, str]:
    """
    Returns:
      (True, "OK") → run LangGraph
      (False, reason) → skip safely
    """

    if has_application(job_id, candidate_id):
        return False, "Already applied"

    if is_archived(job_id, candidate_id):
        return False, "Job archived"

    if has_skip_decision(job_id, candidate_id):
        return False, "Previously skipped"

    # HOLD is a *soft* stop — configurable
    if is_on_hold(job_id, candidate_id):
        return False, "Job on hold"

    return True, "OK"
