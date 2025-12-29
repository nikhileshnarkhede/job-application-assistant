# Email Generator Subgraph

Generates recruiter outreach emails for various purposes.

## Overview

The Email Generator subgraph creates professional emails for:
- Cold outreach to recruiters
- Application follow-ups
- Thank you notes after interviews
- Referral requests
- General networking

## Graph Flow

```
START ──► prepare_context ──► select_template ──► generate_email ──► format_output ──► END
```

## Usage

```python
from subgraphs import (
    generate_outreach_email,
    generate_cold_outreach,
    generate_followup_email,
    generate_thank_you_email,
    get_email_text,
    EmailType,
    EmailTone
)

# General outreach
result = generate_outreach_email(
    structured_jd=jd,
    resume_json=resume,
    email_type=EmailType.COLD_OUTREACH,
    tone=EmailTone.PROFESSIONAL
)
email = result["generated_email"]

# Cold outreach (convenience)
result = generate_cold_outreach(
    structured_jd=jd,
    resume_json=resume,
    recruiter_name="Jane Smith",
    how_found="LinkedIn"
)

# Follow-up email
result = generate_followup_email(
    structured_jd=jd,
    resume_json=resume,
    application_date="December 15, 2024",
    recruiter_name="Recruiting Team"
)

# Thank you email
result = generate_thank_you_email(
    structured_jd=jd,
    resume_json=resume,
    interviewer_name="John Doe",
    interview_date="today",
    custom_context="Enjoyed discussing the ML pipeline project"
)

# Get plain text
text = get_email_text(email)
```

## Output: GeneratedEmail

```python
GeneratedEmail(
    full_text="Subject: Application for ML Engineer...\n\nDear Jane,\n\n...",
    subject="Application for Machine Learning Engineer - John Doe",
    recipient_name="Jane Smith",
    recipient_company="Amazon",
    word_count=150,
    personalization_score=85.0,
    has_clear_ask=True,
    has_value_proposition=True,
    subject_alternatives=[
        "ML Engineer with 5+ Years Experience",
        "Experienced ML Professional Interested in AWS Team"
    ]
)
```

## Email Types

| Type | Description |
|------|-------------|
| `COLD_OUTREACH` | Initial contact with recruiter |
| `APPLICATION_FOLLOWUP` | Follow up after applying |
| `THANK_YOU` | Post-interview thanks |
| `REFERRAL_REQUEST` | Asking for referral |
| `NETWORKING` | General networking |

## Email Tones

| Tone | Description |
|------|-------------|
| `PROFESSIONAL` | Formal, business-like |
| `ENTHUSIASTIC` | Energetic, excited |
| `CONVERSATIONAL` | Friendly, approachable |

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | EmailGeneratorState, GeneratedEmail, EmailType, EmailTone, EmailRecipient |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `prompts/` | LLM prompts for each email type |
| `test.py` | Test script |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `generate_outreach_email(...)` | Full control over generation |
| `generate_cold_outreach(...)` | Cold outreach shortcut |
| `generate_followup_email(...)` | Follow-up shortcut |
| `generate_thank_you_email(...)` | Thank you shortcut |
| `get_email_text(email)` | Extract plain text |
| `get_email_summary(email)` | Stats summary |

## Return Value

```python
{
    "generated_email": GeneratedEmail,  # Generated email
    "generation_complete": bool,
    "error": str | None
}
```

## Email Best Practices

1. **Subject line**: Clear, specific, includes role
2. **Opening**: Personalized, not generic
3. **Value proposition**: What you offer
4. **Clear ask**: Specific next step
5. **Length**: 100-200 words
6. **Signature**: Name, phone, LinkedIn
