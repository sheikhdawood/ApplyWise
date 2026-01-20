import time
import random
from typing import Dict, Any
from playwright.sync_api import sync_playwright, TimeoutError
from db.repositories import save_application 

def human_delay(min_s=2, max_s=5):
    time.sleep(random.uniform(min_s, max_s))

def detect_captcha(page) -> bool:
    text = page.content().lower()
    return any(k in text for k in ["captcha", "verify you are human"])

def detect_login_wall(page) -> bool:
    text = page.content().lower()
    return any(k in text for k in ["sign in", "log in to continue"])

def apply_via_form(page, job, resume_path, cover_letter_text) -> None:
    upload_inputs = page.locator("input[type='file']")
    if upload_inputs.count() > 0:
        upload_inputs.first.set_input_files(resume_path)
        human_delay()

    if cover_letter_text:
        textareas = page.locator("textarea")
        if textareas.count() > 0:
            textareas.first.fill(cover_letter_text)
            human_delay()

    submit_buttons = page.locator(
        "button:has-text('Submit'), button:has-text('Apply')"
    )
    if submit_buttons.count() == 0:
        raise RuntimeError("Submit button not found")

    submit_buttons.first.click()
    human_delay(4, 7)

def apply_node(state: Dict[str, Any]) -> Dict[str, Any]:

    job = state["job_posting"]
    decision = state["application_decision"]
    trust = state.get("platform_trust", {})

    candidate_id = state["candidate_profile"].get("candidate_id", "default")

    # ---------- SAFETY GATE ----------
    if decision.get("requires_human") and trust.get("automation_level") != "FULL":
        result = {
            "status": "ABORTED",
            "error": "Automation not trusted yet",
            "platform": job.get("platform")
        }
        save_application(job["job_id"], candidate_id, result)  # ✅ DB
        return {"application_result": result}

    resume_path = (
        state["resume_variant"].get("file_path")
        if state.get("resume_variant")
        else state["resume_artifact"].get("file_path")
    )

    cover_letter_text = (
        state.get("cover_letter", {}).get("text")
        if state.get("cover_letter")
        else None
    )

    browser = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            page.goto(job["job_url"], timeout=30000)
            human_delay()

            # ---------- HARD STOPS ----------
            if detect_captcha(page):
                result = {
                    "status": "ABORTED",
                    "error": "CAPTCHA detected",
                    "platform": job.get("platform")
                }
                save_application(job["job_id"], candidate_id, result)  # ✅ DB
                return {"application_result": result}

            if detect_login_wall(page):
                result = {
                    "status": "ABORTED",
                    "error": "Login wall detected",
                    "platform": job.get("platform")
                }
                save_application(job["job_id"], candidate_id, result)  # ✅ DB
                return {"application_result": result}

            # ---------- APPLY ----------
            apply_via_form(
                page=page,
                job=job,
                resume_path=resume_path,
                cover_letter_text=cover_letter_text
            )

            result = {
                "status": "SUCCESS",
                "error": None,
                "platform": job.get("platform")
            }
            save_application(job["job_id"], candidate_id, result)  # ✅ DB
            return {"application_result": result}

    except TimeoutError:
        result = {
            "status": "FAILED",
            "error": "Timeout during application",
            "platform": job.get("platform")
        }
        save_application(job["job_id"], candidate_id, result)  # ✅ DB
        return {"application_result": result}

    except Exception as e:
        result = {
            "status": "FAILED",
            "error": str(e),
            "platform": job.get("platform")
        }
        save_application(job["job_id"], candidate_id, result)  # ✅ DB
        return {"application_result": result}

    finally:
        if browser:
            browser.close()
