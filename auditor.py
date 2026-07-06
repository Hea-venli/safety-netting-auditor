# Safety-Netting Auditor - version 1
# Reads a clinical note and checks the safety-netting advice.

def read_note(filepath):
    """Open a note file and return its text."""
    with open(filepath, "r") as file:
        text = file.read()
    return text


# Words/phrases that signal safety-netting advice is present
SAFETY_KEYWORDS = [
    "safety-netting",
    "safety netting",
    "return to a&e",
    "come back",
    "call 999",
    "call gp",
    "contact gp",
    "see your gp",
    "nhs 111",
    "seek help",
    "go to a&e",
]

def has_safety_netting(text):
    """Return True if the note contains any safety-netting phrases."""

    text_lower = text.lower()
    for keyword in SAFETY_KEYWORDS:
        if keyword in text_lower:
            return True
    return False


# Signs of SPECIFIC (good) safety-netting - specific symptoms and escalation routes
SPECIFIC_KEYWORDS = [
    "999",
    "a&e",
    "nhs 111",
    "blue lips",
    "confusion",
    "drowsiness",
    "drowsy",
    "chest pain",
    "coughing up blood",
    "breathing fast",
    "breathless",
    "ketones",
    "vomiting",
    "fever returns",
    "not improving after",
    "within 48 hours",
    "within 1 week",
]

def grade_safety_netting(text):
    """Grade the note: GOOD, VAGUE, or MISSING."""
    if not has_safety_netting(text):
        return "MISSING"
    text_lower = text.lower()
    specific_count = 0
    for keyword in SPECIFIC_KEYWORDS:
        if keyword in text_lower:
            specific_count = specific_count + 1
    if specific_count >= 3:
        return "GOOD"
    else:
        return "VAGUE"


# --- AI LAYER ---
import boto3
import json

client = boto3.client("bedrock-runtime", region_name="eu-west-2")

AUDIT_PROMPT = """You are a clinical documentation auditor reviewing discharge notes.

Assess the SAFETY-NETTING advice in the note below. Safety-netting means the
advice telling the patient what warning signs to watch for and when/where to
seek help (e.g. specific symptoms, timeframes, escalation routes like GP/111/999/A&E).

Grade it as exactly one of:
- GOOD: specific warning signs AND a clear escalation route
- VAGUE: some advice present but non-specific (e.g. "come back if worse")
- MISSING: no safety-netting advice at all

Reply in exactly this format:
GRADE: <GOOD or VAGUE or MISSING>
REASON: <one sentence explaining why>

Note to audit:
"""

def ai_grade(text):
    """Ask Claude (via AWS Bedrock) to grade the note's safety-netting."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": AUDIT_PROMPT + text}]
    })
    response = client.invoke_model(
        modelId="anthropic.claude-sonnet-4-6",
        body=body
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

if __name__ == "__main__":
    import os

    print("\n--- RULES GRADES ---")
    for filename in sorted(os.listdir("notes")):
        note_text = read_note("notes/" + filename)
        print(filename, "->", grade_safety_netting(note_text))

    print("\n--- AI GRADES ---")
    for filename in sorted(os.listdir("notes")):
        note_text = read_note("notes/" + filename)
        print("\n" + filename)
        print(ai_grade(note_text))


def lambda_handler(event, context):
    """AWS Lambda entry point: receive a note via API, return the AI grade."""
    body = json.loads(event.get("body", "{}"))
    note_text = body.get("note", "")

    if not note_text:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No note text provided. Send JSON: {\"note\": \"...\"}"})
        }

    result = ai_grade(note_text)
    return {
        "statusCode": 200,
        "body": json.dumps({"result": result})
    }
