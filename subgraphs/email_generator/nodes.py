"""
Email Generator Nodes

Generates professional outreach emails for job search.

Nodes:
1. prepare_context - Gather all context for email generation
2. select_template - Choose appropriate template based on email type
3. generate_email - Generate email using LLM
4. format_output - Format and validate final email
"""

import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from subgraphs.email_generator.state import (
    EmailGeneratorState,
    EmailType,
    EmailTone,
    EmailRecipient,
    GeneratedEmail,
    EMAIL_GUIDELINES
)

# Load candidate profile
try:
    from data.candidate_profile import candidate_profile
except ImportError:
    candidate_profile = None


# ============================================================================
# CONFIGURATION
# ============================================================================

def get_llm():
    """Get configured LLM instance."""
    if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            temperature=0.7,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )


def load_prompt(filename: str) -> str:
    """Load prompt from file."""
    prompt_dir = Path(__file__).parent / "prompts"
    prompt_path = prompt_dir / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# NODE 1: PREPARE CONTEXT
# ============================================================================

def prepare_context(state: EmailGeneratorState) -> Dict[str, Any]:
    """
    Gather all context needed for email generation.
    """
    jd = state.structured_jd
    resume = state.resume_json
    recipient = state.recipient
    
    print(f"  📧 Preparing context for {state.email_type.value} email...")
    
    context = {
        "email_type": state.email_type.value,
        "tone": state.tone.value,
        "custom_context": state.custom_context or "",
    }
    
    # Recipient info
    if recipient:
        context["recipient"] = {
            "name": recipient.name or "Hiring Manager",
            "title": recipient.title or "",
            "company": recipient.company or "",
            "how_found": recipient.how_found or "",
            "mutual_connections": recipient.mutual_connections or [],
            "notes": recipient.notes or ""
        }
    else:
        context["recipient"] = {
            "name": "Hiring Manager",
            "title": "",
            "company": jd.company_name if jd else "",
            "how_found": "",
            "mutual_connections": [],
            "notes": ""
        }
    
    # Job info from JD
    if jd:
        context["job"] = {
            "company": jd.company_name,
            "role": jd.role_title,
            "location": jd.location or "",
            "key_requirements": (jd.skills_required or [])[:5],
            "responsibilities": (jd.responsibilities or [])[:3]
        }
    else:
        context["job"] = {
            "company": context["recipient"]["company"],
            "role": "",
            "location": "",
            "key_requirements": [],
            "responsibilities": []
        }
    
    # Candidate info from resume or profile
    if resume:
        header = resume.header or {}
        context["candidate"] = {
            "name": header.get("name", ""),
            "email": header.get("email", ""),
            "phone": header.get("phone", ""),
            "location": header.get("location", ""),
            "role": "",
            "qualifications": [],
            "top_achievement": ""
        }
        
        # Get current role
        if resume.experience:
            first_exp = resume.experience[0]
            context["candidate"]["role"] = f"{first_exp.get('role', '')} at {first_exp.get('company', '')}"
            
            # Get top achievement (bullet with metrics)
            for exp in resume.experience[:2]:
                for bullet in exp.get("bullets", []):
                    if any(c.isdigit() for c in bullet):
                        context["candidate"]["top_achievement"] = bullet
                        break
                if context["candidate"]["top_achievement"]:
                    break
        
        # Get key qualifications
        all_skills = []
        for category, skills in (resume.skills or {}).items():
            all_skills.extend(skills.split(", ")[:3])
        context["candidate"]["qualifications"] = all_skills[:5]
        
    elif candidate_profile:
        context["candidate"] = {
            "name": candidate_profile.get("name", ""),
            "email": candidate_profile.get("email", ""),
            "phone": candidate_profile.get("phone", ""),
            "location": candidate_profile.get("location", ""),
            "role": "",
            "qualifications": [],
            "top_achievement": ""
        }
    else:
        context["candidate"] = {
            "name": "Candidate",
            "email": "",
            "phone": "",
            "location": "",
            "role": "",
            "qualifications": [],
            "top_achievement": ""
        }
    
    # Type-specific info
    if state.email_type == EmailType.APPLICATION_FOLLOWUP:
        context["application_date"] = state.application_date or "recently"
    elif state.email_type == EmailType.THANK_YOU:
        context["interview_date"] = state.interview_date or "today"
    elif state.email_type == EmailType.REFERRAL_REQUEST:
        context["referral_name"] = state.referral_name or ""
    
    print(f"  ✅ Context prepared for {context['recipient']['name']} at {context['job']['company']}")
    
    return {"context_data": context}


# ============================================================================
# NODE 2: SELECT TEMPLATE
# ============================================================================

def select_template(state: EmailGeneratorState) -> Dict[str, Any]:
    """
    Select appropriate email template and guidelines based on type.
    """
    email_type = state.email_type.value
    
    print(f"  📋 Selecting template for: {email_type}")
    
    guidelines = EMAIL_GUIDELINES.get(email_type, EMAIL_GUIDELINES["cold_outreach"])
    
    template_info = {
        "email_type": email_type,
        "subject_templates": guidelines.get("subject_templates", []),
        "ideal_length": guidelines.get("ideal_length", (100, 150)),
        "key_elements": guidelines.get("key_elements", []),
        "avoid": guidelines.get("avoid", []),
        "timing": guidelines.get("timing", "")
    }
    
    print(f"  ✅ Template selected: {template_info['ideal_length'][0]}-{template_info['ideal_length'][1]} words")
    
    return {"template_info": template_info}


# ============================================================================
# NODE 3: GENERATE EMAIL
# ============================================================================

def generate_email(state: EmailGeneratorState) -> Dict[str, Any]:
    """
    Generate email using LLM.
    """
    context = state.context_data
    template_info = state.template_info
    
    if not context:
        return {"error_message": "No context prepared"}
    
    print(f"  ✍️ Generating {state.email_type.value} email...")
    
    # Load prompts
    system_prompt = load_prompt("system_prompt.txt")
    generation_prompt = load_prompt("generation_prompt.txt")
    few_shot = load_prompt("few_shot_examples.txt")
    
    # Type-specific info
    type_specific = ""
    if state.email_type == EmailType.APPLICATION_FOLLOWUP:
        type_specific = f"Application Date: {context.get('application_date', 'recently')}"
    elif state.email_type == EmailType.THANK_YOU:
        type_specific = f"Interview Date: {context.get('interview_date', 'today')}"
    elif state.email_type == EmailType.REFERRAL_REQUEST:
        type_specific = f"Referral Connection: {context.get('referral_name', 'N/A')}"
    
    # Format prompt
    ideal_length = template_info.get('ideal_length', (100, 150))
    
    try:
        user_prompt = generation_prompt.format(
            email_type=state.email_type.value.replace("_", " ").title(),
            email_type_upper=state.email_type.value.upper(),
            recipient_name=context.get("recipient", {}).get("name", "Hiring Manager"),
            recipient_title=context.get("recipient", {}).get("title", ""),
            recipient_company=context.get("recipient", {}).get("company", ""),
            how_found=context.get("recipient", {}).get("how_found", ""),
            mutual_connections=", ".join(context.get("recipient", {}).get("mutual_connections", [])) or "None",
            recipient_notes=context.get("recipient", {}).get("notes", ""),
            candidate_name=context.get("candidate", {}).get("name", "Candidate"),
            candidate_role=context.get("candidate", {}).get("role", ""),
            candidate_location=context.get("candidate", {}).get("location", ""),
            candidate_qualifications=", ".join(context.get("candidate", {}).get("qualifications", [])),
            top_achievement=context.get("candidate", {}).get("top_achievement", ""),
            company_name=context.get("job", {}).get("company", ""),
            role_title=context.get("job", {}).get("role", ""),
            job_location=context.get("job", {}).get("location", ""),
            key_requirements=", ".join(context.get("job", {}).get("key_requirements", [])),
            tone=state.tone.value,
            custom_context=state.custom_context or "None",
            type_specific_info=type_specific,
            ideal_length=f"{ideal_length[0]}-{ideal_length[1]}",
            key_elements="\n".join(f"- {elem}" for elem in template_info.get("key_elements", [])),
            avoid_elements="\n".join(f"- {elem}" for elem in template_info.get("avoid", []))
        )
    except Exception as e:
        print(f"  ❌ Prompt formatting failed: {e}")
        return {"error_message": f"Prompt formatting failed: {e}"}
    
    try:
        llm = get_llm()
        messages = [
            SystemMessage(content=f"{system_prompt}\n\n{few_shot}"),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        email = parse_email_response(response.content, context, state)
        
        print(f"  ✅ Email generated: {email.word_count} words")
        
        return {"generated_email": email}
        
    except Exception as e:
        print(f"  ❌ LLM generation failed: {e}")
        return {"error_message": str(e)}


def parse_email_response(response: str, context: Dict, state: EmailGeneratorState) -> GeneratedEmail:
    """Parse LLM response into GeneratedEmail object."""
    
    email = GeneratedEmail(
        email_type=state.email_type.value,
        tone=state.tone.value,
        recipient_name=context.get("recipient", {}).get("name", ""),
        recipient_company=context.get("recipient", {}).get("company", "")
    )
    
    # Extract subject
    subject_match = re.search(r'SUBJECT:\s*(.+?)(?:\n|SUBJECT_ALT)', response, re.IGNORECASE)
    if subject_match:
        email.subject = subject_match.group(1).strip()
    
    # Extract alternative subjects
    alt_subjects = re.findall(r'SUBJECT_ALT_\d+:\s*(.+?)(?:\n|---)', response, re.IGNORECASE)
    email.subject_alternatives = [s.strip() for s in alt_subjects]
    
    # Extract body (between greeting and sign-off)
    body_match = re.search(r'(Hi|Hello|Dear)[^\n]*,\s*\n\n(.+?)\n\n(Best|Sincerely|Thank|Regards)', 
                          response, re.DOTALL | re.IGNORECASE)
    if body_match:
        recipient_name = context.get("recipient", {}).get("name", "Hiring Manager")
        first_name = recipient_name.split()[0] if recipient_name else "there"
        email.greeting = body_match.group(1) + " " + first_name + ","
        email.body = body_match.group(2).strip()
        email.closing = ""
    
    # Extract has clear ask
    ask_match = re.search(r'HAS_CLEAR_ASK:\s*(YES|NO)', response, re.IGNORECASE)
    email.has_clear_ask = ask_match and ask_match.group(1).upper() == "YES"
    
    # Extract has value proposition
    value_match = re.search(r'HAS_VALUE_PROPOSITION:\s*(YES|NO)', response, re.IGNORECASE)
    email.has_value_proposition = value_match and value_match.group(1).upper() == "YES"
    
    # Create full text - find the actual email content
    lines = response.split('\n')
    email_lines = []
    in_email = False
    for line in lines:
        if line.strip().startswith(('Hi ', 'Hello ', 'Dear ')):
            in_email = True
        if in_email:
            if line.strip().startswith(('WORD_COUNT', 'HAS_CLEAR', 'HAS_VALUE', 'PERSONALIZATION')):
                break
            email_lines.append(line)
    
    full_text = '\n'.join(email_lines).strip()
    
    # Clean up
    full_text = re.sub(r'---+', '', full_text)
    full_text = full_text.strip()
    
    # If we couldn't parse the email properly, use the raw response
    if not full_text or len(full_text) < 50:
        # Try to extract just the email portion
        start_idx = response.find("Hi ") or response.find("Hello ") or response.find("Dear ")
        if start_idx == -1:
            start_idx = 0
        full_text = response[start_idx:].strip()
        # Remove metadata at the end
        for marker in ['WORD_COUNT', 'HAS_CLEAR', 'HAS_VALUE', 'PERSONALIZATION']:
            idx = full_text.find(marker)
            if idx != -1:
                full_text = full_text[:idx].strip()
    
    email.full_text = full_text
    email.word_count = len(full_text.split())
    
    # Calculate personalization score
    score = 0
    recipient_name = context.get("recipient", {}).get("name", "")
    if recipient_name and recipient_name != "Hiring Manager":
        score += 25
    company = context.get("job", {}).get("company", "")
    if company and company.lower() in full_text.lower():
        score += 25
    role = context.get("job", {}).get("role", "")
    if role and any(w in full_text.lower() for w in role.lower().split() if len(w) > 3):
        score += 20
    if email.has_clear_ask:
        score += 15
    if email.has_value_proposition:
        score += 15
    
    email.personalization_score = min(100, score)
    
    return email


# ============================================================================
# NODE 4: FORMAT OUTPUT
# ============================================================================

def format_output(state: EmailGeneratorState) -> Dict[str, Any]:
    """
    Format and validate final email output.
    """
    email = state.generated_email
    
    if not email:
        return {"error_message": "No email generated"}
    
    print(f"  📄 Formatting final email...")
    
    # Ensure we have a subject
    if not email.subject:
        jd = state.structured_jd
        if jd:
            email.subject = f"{jd.role_title} Opportunity - Inquiry"
        else:
            email.subject = "Career Opportunity Inquiry"
    
    # Validate word count
    guidelines = EMAIL_GUIDELINES.get(state.email_type.value, {})
    ideal = guidelines.get("ideal_length", (100, 150))
    
    word_status = "optimal"
    if email.word_count < ideal[0]:
        word_status = "short"
    elif email.word_count > ideal[1]:
        word_status = "long"
    
    print(f"  ✅ Email ready: {email.word_count} words ({word_status})")
    print(f"     Subject: {email.subject[:50]}...")
    print(f"     Personalization: {email.personalization_score:.0f}%")
    
    return {
        "generated_email": email,
        "generation_complete": True
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "prepare_context",
    "select_template",
    "generate_email",
    "format_output",
    "get_llm",
    "load_prompt"
]
