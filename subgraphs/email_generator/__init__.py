"""
Email Generator Subgraph

Generates professional outreach emails for job search:
1. Cold outreach to recruiters
2. Application follow-ups
3. Referral requests
4. Thank you after interviews
5. Networking emails

Usage:
    from subgraphs.email_generator import (
        generate_outreach_email,
        generate_cold_outreach,
        generate_followup_email,
        generate_thank_you_email,
        EmailType,
        EmailRecipient
    )
    
    # Cold outreach
    result = generate_cold_outreach(
        structured_jd=structured_jd,
        resume_json=resume_json,
        recruiter_name="Sarah Chen",
        recruiter_title="Technical Recruiter"
    )
    
    email = result["generated_email"]
    print(email.full_text)
    
    # Follow-up
    result = generate_followup_email(
        structured_jd=structured_jd,
        resume_json=resume_json,
        application_date="January 15, 2024"
    )
"""

from subgraphs.email_generator.graph import (
    build_email_generator_graph,
    create_email_generator_subgraph,
    generate_outreach_email,
    generate_cold_outreach,
    generate_followup_email,
    generate_thank_you_email,
    get_email_text,
    get_email_summary
)

from subgraphs.email_generator.state import (
    EmailGeneratorState,
    EmailType,
    EmailTone,
    EmailRecipient,
    GeneratedEmail,
    EMAIL_GUIDELINES
)

from subgraphs.email_generator.nodes import (
    prepare_context,
    select_template,
    generate_email,
    format_output
)

__all__ = [
    # Main functions
    "generate_outreach_email",
    "generate_cold_outreach",
    "generate_followup_email",
    "generate_thank_you_email",
    "get_email_text",
    "get_email_summary",
    
    # Graph builders
    "build_email_generator_graph",
    "create_email_generator_subgraph",
    
    # State & Models
    "EmailGeneratorState",
    "EmailType",
    "EmailTone",
    "EmailRecipient",
    "GeneratedEmail",
    "EMAIL_GUIDELINES",
    
    # Nodes
    "prepare_context",
    "select_template",
    "generate_email",
    "format_output"
]
