from typing import Dict, Any
from db.repositories import save_trust_state

def trust_update_node(state: Dict[str, Any]) -> Dict[str, Any]:

    result = state["application_result"]
    job = state["job_posting"]

    platform = job.get("platform", "UNKNOWN")

    # ---------- INITIAL TRUST STATE ----------
    trust = state.get("platform_trust", {
        "trust_score": 5,
        "automation_level": "LIMITED",
        "signals": {
            "successful_apps": 0,
            "failed_apps": 0,
            "captcha_hits": 0,
            "warnings": 0
        }
    })

    kill_switch = False

    # ---------- POSITIVE SIGNALS ----------
    if result["status"] == "SUCCESS":
        trust["trust_score"] += 2
        trust["signals"]["successful_apps"] += 1

        # Clean run bonus
        trust["trust_score"] += 1

    # ---------- NEGATIVE SIGNALS ----------
    if result["status"] == "FAILED":
        trust["trust_score"] -= 2
        trust["signals"]["failed_apps"] += 1

    error = (result.get("error") or "").lower()

    if "captcha" in error:
        trust["trust_score"] -= 7
        trust["signals"]["captcha_hits"] += 1

    if "login" in error:
        trust["trust_score"] -= 6

    if "warning" in error:
        trust["trust_score"] -= 10
        trust["signals"]["warnings"] += 1
        kill_switch = True

    # ---------- BOUND TRUST SCORE ----------
    trust["trust_score"] = max(trust["trust_score"], 0)

    # ---------- AUTOMATION ESCALATION ----------
    if trust["trust_score"] >= 15 and trust["signals"]["captcha_hits"] == 0:
        trust["automation_level"] = "FULL"
    else:
        trust["automation_level"] = "LIMITED"

    # ---------- KILL SWITCH CONDITIONS ----------
    if trust["signals"]["captcha_hits"] >= 2:
        kill_switch = True

    if trust["trust_score"] == 0:
        kill_switch = True

    # ✅ PERSIST TRUST STATE
    save_trust_state(platform, trust)

    return {
        "platform_trust": trust,
        "kill_switch": kill_switch
    }
