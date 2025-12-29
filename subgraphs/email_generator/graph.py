"""
Email Generator Subgraph Builder

Generates professional outreach emails for job search.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────────┐
│    prepare_context      │  ← Gather candidate, job, recipient info
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    select_template      │  ← Choose email type template
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    generate_email       │  ← LLM generates personalized email
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     format_output       │  ← Validate and format
└───────────┬─────────────┘
            │
            ▼
          END
```
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from subgraphs.email_generator.state import (
    EmailGeneratorState,
    EmailType,
    EmailTone,
    EmailRecipient,
    GeneratedEmail
)
from subgraphs.email_generator.nodes import (
    prepare_context,
    select_template,
    generate_email,
    format_output
)


def build_email_generator_graph() -> StateGraph:
    """
    Build the Email Generator subgraph.
    
    Returns:
        Compiled StateGraph for email generation
    """
    graph = StateGraph(EmailGeneratorState)
    
    # Add nodes
    graph.add_node("prepare_context", prepare_context)
    graph.add_node("select_template", select_template)
    graph.add_node("generate_email", generate_email)
    graph.add_node("format_output", format_output)
    
    # Add edges
    graph.add_edge(START, "prepare_context")
    graph.add_edge("prepare_context", "select_template")
    graph.add_edge("select_template", "generate_email")
    graph.add_edge("generate_email", "format_output")
    graph.add_edge("format_output", END)
    
    return graph.compile()


def create_email_generator_subgraph():
    """Create and return the compiled Email Generator subgraph."""
    return build_email_generator_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def generate_outreach_email(
    structured_jd=None,
    resume_json=None,
    recipient: EmailRecipient = None,
    email_type: EmailType = EmailType.COLD_OUTREACH,
    tone: EmailTone = EmailTone.PROFESSIONAL,
    custom_context: str = "",
    application_date: str = None,
    interview_date: str = None,
    referral_name: str = None
) -> Dict[str, Any]:
    """
    Generate a professional outreach email.
    
    Args:
        structured_jd: StructuredJD object (optional)
        resume_json: ResumeJSON object (optional)
        recipient: EmailRecipient with recipient details
        email_type: Type of email (cold_outreach, follow_up, etc.)
        tone: Email tone (professional, friendly, etc.)
        custom_context: Additional context for personalization
        application_date: Date of application (for follow-ups)
        interview_date: Date of interview (for thank yous)
        referral_name: Name of referrer (for referral requests)
    
    Returns:
        Dict with generated_email and generation status
    """
    graph = create_email_generator_subgraph()
    
    initial_state = {
        "structured_jd": structured_jd,
        "resume_json": resume_json,
        "recipient": recipient,
        "email_type": email_type,
        "tone": tone,
        "custom_context": custom_context,
        "application_date": application_date,
        "interview_date": interview_date,
        "referral_name": referral_name
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "generated_email": result.get("generated_email"),
        "generation_complete": result.get("generation_complete", False),
        "error": result.get("error_message")
    }


def generate_cold_outreach(
    structured_jd,
    resume_json,
    recruiter_name: str = "Hiring Manager",
    recruiter_title: str = "",
    how_found: str = "LinkedIn"
) -> Dict[str, Any]:
    """
    Quick function to generate cold outreach email.
    
    Args:
        structured_jd: StructuredJD object
        resume_json: ResumeJSON object
        recruiter_name: Name of recruiter
        recruiter_title: Title of recruiter
        how_found: How you found them
    
    Returns:
        Dict with generated_email
    """
    recipient = EmailRecipient(
        name=recruiter_name,
        title=recruiter_title,
        company=structured_jd.company_name if structured_jd else "",
        how_found=how_found
    )
    
    return generate_outreach_email(
        structured_jd=structured_jd,
        resume_json=resume_json,
        recipient=recipient,
        email_type=EmailType.COLD_OUTREACH,
        tone=EmailTone.PROFESSIONAL
    )


def generate_followup_email(
    structured_jd,
    resume_json,
    application_date: str,
    recruiter_name: str = "Recruiting Team"
) -> Dict[str, Any]:
    """
    Quick function to generate application follow-up email.
    
    Args:
        structured_jd: StructuredJD object
        resume_json: ResumeJSON object
        application_date: When you applied
        recruiter_name: Name of contact
    
    Returns:
        Dict with generated_email
    """
    recipient = EmailRecipient(
        name=recruiter_name,
        company=structured_jd.company_name if structured_jd else ""
    )
    
    return generate_outreach_email(
        structured_jd=structured_jd,
        resume_json=resume_json,
        recipient=recipient,
        email_type=EmailType.APPLICATION_FOLLOWUP,
        application_date=application_date
    )


def generate_thank_you_email(
    structured_jd,
    resume_json,
    interviewer_name: str,
    interview_date: str = "today",
    custom_context: str = ""
) -> Dict[str, Any]:
    """
    Quick function to generate thank you email after interview.
    
    Args:
        structured_jd: StructuredJD object
        resume_json: ResumeJSON object
        interviewer_name: Name of interviewer
        interview_date: When interview occurred
        custom_context: Specific topics discussed
    
    Returns:
        Dict with generated_email
    """
    recipient = EmailRecipient(
        name=interviewer_name,
        company=structured_jd.company_name if structured_jd else ""
    )
    
    return generate_outreach_email(
        structured_jd=structured_jd,
        resume_json=resume_json,
        recipient=recipient,
        email_type=EmailType.THANK_YOU,
        interview_date=interview_date,
        custom_context=custom_context
    )


def get_email_text(email: GeneratedEmail) -> str:
    """Get the full text of an email."""
    if not email:
        return ""
    return email.full_text


def get_email_summary(email: GeneratedEmail) -> str:
    """Generate a summary of the generated email."""
    if not email:
        return "No email generated."
    
    lines = [
        "=" * 50,
        "EMAIL SUMMARY",
        "=" * 50,
        "",
        f"📧 Type: {email.email_type.replace('_', ' ').title()}",
        f"👤 To: {email.recipient_name} at {email.recipient_company}",
        f"📝 Subject: {email.subject}",
        "",
        f"📊 Statistics:",
        f"   Word Count: {email.word_count}",
        f"   Personalization: {email.personalization_score:.0f}%",
        f"   Clear Ask: {'✅' if email.has_clear_ask else '❌'}",
        f"   Value Proposition: {'✅' if email.has_value_proposition else '❌'}",
        "",
    ]
    
    if email.subject_alternatives:
        lines.append("📋 Alternative Subjects:")
        for i, alt in enumerate(email.subject_alternatives[:2], 1):
            lines.append(f"   {i}. {alt}")
        lines.append("")
    
    lines.append("=" * 50)
    
    return "\n".join(lines)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_email_generator_graph",
    "create_email_generator_subgraph",
    "generate_outreach_email",
    "generate_cold_outreach",
    "generate_followup_email",
    "generate_thank_you_email",
    "get_email_text",
    "get_email_summary"
]
