# AI Safety-Netting Auditor

A tool that checks hospital discharge notes for safety-netting advice (the instructions telling a patient what warning signs to watch for after leaving hospital, and when and where to seek help). It grades the advice in each note as GOOD, VAGUE, or MISSING.

I designed and clinically authored this project. I am a GMC-registered Physician Associate with two and a half years in acute NHS medicine, and I built it with AI assistance (Claude) and deployed it on AWS. It flags gaps for a clinician to review. It does not advise patients or make clinical decisions.

🎬 **90-second demo:** *(link coming soon)*
🔗 **Related project:** [Cloud Cost Optimiser](https://github.com/Hea-venli/cloud-cost-optimiser)

## Why this problem

During my clinical work I regularly saw safety-netting advice given to a patient verbally but not written into the discharge note. The research shows this is common:

| Finding | Source |
|---|---|
| Safety-netting advice spoken in GP consultations was documented in the notes only 46.9% of the time | [Edwards et al., BJGP 2021](https://bjgp.org/content/71/712/e869) |
| Around one in five out-of-hours consultations had no documented safety-netting advice | [BJGP 2025 retrospective cohort](https://bjgp.org/content/75/751/e80) |
| Discharge summaries met around 55% of core content criteria in one hospital audit (single trust) | [Chowdhury et al., BMJ Open Quality 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8991046/) |
| The national safety investigator found poor discharge communication has become "normalised", with documented patient harm | [HSSIB investigation, July 2025](https://www.hssib.org.uk/news-events-blog/investigation-finds-patients-suffer-harm-as-electronic-communications-fail-to-support-their-safe-discharge-from-hospital/) |
| Around 53% of patients experience a medication error after discharge; around 19% an adverse drug event | [Alqenae et al., Drug Safety 2020](https://link.springer.com/article/10.1007/s40264-020-00918-3) |
| 14.8% of emergency admissions in 2023/24 were readmissions within 30 days of discharge | [CQC, State of Care 2024/25](https://www.cqc.org.uk/publications/major-report/state-care/2024-2025/access/secondary) |
| England records around 17.6 million hospital admissions a year | [NHS Hospital Episode Statistics 2023–24](https://digital.nhs.uk/data-and-information/publications/statistical/hospital-admitted-patient-care-activity/2023-24) |

## How it works

The auditor has two layers.

The rules layer runs first. It is a Python keyword checker that looks for safety-netting phrases and grades the note. It is instant, free to run, and fully explainable, so clear-cut cases never need the AI at all.

The AI layer runs second. Claude, called through Amazon Bedrock, reads the note and grades it GOOD, VAGUE or MISSING with a one-line reason. This layer exists because keyword matching has a real limitation I hit during testing: my keyword list contained "breathless", a test note said "shortness of breath", and the rules layer missed it. The two phrases mean the same thing clinically but do not match as text. The AI layer handles meaning rather than exact wording.

The prompt forces a fixed output format (a grade, then a reason) so the response can be parsed reliably by code rather than read as free text.

## Safety decisions

Three decisions were made at the design stage.

The tool audits documents only. Its output goes to a clinician, who decides what to do. It does not give advice to patients.

It runs on synthetic data only. All five test notes (COPD, pneumonia, asthma, DKA, Graves' disease) were written by me, based on clinical experience. No real patient data has ever been used.

The data stays in one place. Bedrock runs the model inside my AWS region (eu-west-2, London) under IAM authentication, so there are no third-party API keys and nothing is sent outside the account.

### Example

I sent the live endpoint a synthetic discharge note for a patient newly started on carbimazole for Graves' disease, with the safety-netting section deliberately removed. Carbimazole can cause agranulocytosis, a rare but life-threatening drop in white blood cells, so patients must be told to seek urgent help for a sore throat or fever. The tool graded the note MISSING and gave the reason.

## Engineering

| Concern | Implementation |
|---|---|
| Deployment | AWS Lambda behind a Function URL with IAM authorisation; only signed requests from my account can invoke it |
| Infrastructure | Everything defined in Terraform: the Lambda, a least-privilege IAM role, the Function URL, and the monitoring |
| Testing | Six pytest tests cover the rules functions and, using a mocked Bedrock response, the AI function, so the suite runs offline without AWS credentials |
| CI | GitHub Actions runs the tests on every push |
| Monitoring | A CloudWatch alarm on the Lambda's error count publishes to SNS, which emails me |
| Docker | A container image for reproducible batch runs. Credentials are mounted read-only at runtime, never baked into the image. The deployed Lambda itself runs from a zip package; the container is for local use |

## Known limitations and roadmap

I reviewed the codebase after deployment and found the following, listed here with the planned fixes.

Malformed JSON sent to the endpoint crashes the handler and returns a 502, where it should return a 400 with a clear message. The Bedrock call has no error handling, so a model failure also surfaces as a 502. The Bedrock IAM permission currently allows any model (`Resource: "*"`) and should be scoped to the one model ARN in use. The project also needs a requirements file, remote Terraform state, and a Terraform plan step in CI.

The largest gap is evaluation. The tool works, but its grading has not been measured against clinical judgement. The next step is a clinician-graded synthetic evaluation set, scored with percentage agreement and Cohen's kappa, so the AI's accuracy is a number rather than an impression.

If this tool were ever developed for real use, it would need a DPIA, a clinical safety case and hazard log under DCB0129 with a named Clinical Safety Officer, deployment assurance under DCB0160, and DTAC assessment. I have not done that work; I know the requirements from working under NHS clinical governance, and it is the area I want to work in.

Possible product extensions: specialty-specific keyword sets for the rules layer, a batch mode that reports documentation quality at ward level, and prompts built into the discharge workflow itself so the advice is captured when the note is written rather than checked afterwards.

## What building this taught me

Putting a full system together: credential handling, Lambda and Terraform (as in [Project 1](https://github.com/Hea-venli/cloud-cost-optimiser)), Docker, Linux, and CI, built in layers with each one tested before the next was added.

## About the author

GMC-registered Physician Associate (respiratory and endocrine, acute NHS medicine), now working in cloud and AI. AWS Certified Solutions Architect – Associate and Cloud Practitioner.

*This is a personal educational project. It processes synthetic data only and is not a medical device.*
