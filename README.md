# Safety-Netting Auditor

# AI Safety-Netting Auditor

An AI-powered tool that audits hospital discharge summaries for safety-netting
advice — the "return if..." instructions patients need when they're sent home —
grading it GOOD, VAGUE, or MISSING.

Built with AI assistance (Claude), designed and clinically authored by me,
a GMC-registered Physician Associate.

## Why safety-netting matters

Safety-netting is the advice telling a discharged patient what warning signs to
watch for and when and where to seek help. It matters because patients must stay
safe *after* they leave the ward: they need the right instructions and to know
exactly what to do in an emergency. Making sure of that is the clinician's
priority — and when the advice is vague or missing from the notes, patients can
come to harm.

## How it works

1. **Rules first.** A Python keyword checker looks for safety-netting phrases
   and grades the note.
2. **Where rules failed.** Note 1 said "shortness of breath" — my keyword list
   had "breathless." Same clinical meaning, different letters: no match, wrong
   grade. Keyword matching is literal; clinical language isn't.
3. **The AI layer.** An LLM (Claude, via Amazon Bedrock) reads *meaning* — it
   links "shortness of breath" and "breathlessness" as the same thing, and
   grades with clinical reasoning.

## Live deployment

The auditor runs as an AWS Lambda function behind a function URL, locked with
IAM authorisation — only signed requests from my account can invoke it. The
entire stack (Lambda, IAM least-privilege role, function URL, monitoring) is
built with Terraform, the same infrastructure-as-code approach as my
[Cloud Cost Optimiser](https://github.com/Hea-venli/cloud-cost-optimiser).

## Docker

The auditor is packaged in a Docker container, so it can be deployed anytime,
anywhere I choose. AWS credentials are never baked into the image — they're
mounted read-only at runtime.

## Testing & CI

Six pytest tests cover the rules functions and — using a mocked Bedrock
response — the AI function's plumbing, so the suite runs free and offline.
GitHub Actions runs all six on every push: green tick or red X on every commit.

## Monitoring

A CloudWatch alarm watches the Lambda's error count; if it ever errors, SNS
emails me immediately.

## The test data

All five clinical notes (COPD, pneumonia, asthma, DKA, Graves' disease) are
synthetic — written by me from clinical experience, for information-governance
and patient-safety reasons. **No real patient data, ever.**

## Example: catching a dangerous note



## AI suggests, human decides

The tool flags concerns for clinician review — it does not replace clinical
judgement.

## What I learned

How to put different skills together into one system: API keys and credential
discipline, Lambda functions and Terraform (as in Project 1), building a Docker
container, working in Linux — and building in agile-style layers, each one
tested and shipped before the next.

## Skills demonstrated

