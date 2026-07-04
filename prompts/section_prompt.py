SECTION_SYSTEM_PROMPT_BASE = """
You are an expert technical writer.

Your task is to generate a SINGLE section.

Rules:

1. Follow the target word count.
2. Generate content for the section.
3. Generate content for every subsection.
4. Maintain professional tone.
5. Return ONLY JSON.
6. Do not use markdown.
"""

# Keep legacy alias for backwards compatibility
SECTION_SYSTEM_PROMPT = SECTION_SYSTEM_PROMPT_BASE


def build_section_prompt(quality_feedback: str = None) -> str:
    """
    Builds the section system prompt, optionally appending a quality
    correction block when a previous generation attempt was rejected
    by the quality guardrail.

    Args:
        quality_feedback: A feedback string describing what went wrong
                          in the previous attempt, or None for a fresh run.

    Returns:
        The complete system prompt string to pass to the LLM.
    """
    prompt = SECTION_SYSTEM_PROMPT_BASE

    if quality_feedback:
        prompt += f"""
QUALITY CORRECTION (Previous attempt was rejected):
{quality_feedback}

You MUST address this feedback. Do NOT repeat the same mistake.
"""
    return prompt