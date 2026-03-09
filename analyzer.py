import os
from google import genai
from google.genai import types

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please configure it.")
    return genai.Client(api_key=api_key)


def analyze_code(code: str, analysis_type: str, language: str) -> str:
    """
    Analyzes code using the Gemini model based on the requested analysis type.
    """
    client = get_gemini_client()
    
    # We use a solid reasoning model or standard model for text generation based on availability.
    # gemini-2.5-flash is currently a great general-purpose fast model. 
    model_name = "gemini-2.5-flash"
    
    prompts = {
        "Error Detection": (
            f"Analyze the following {language} code specifically to detect errors.\n"
            "Point out every syntax error, logical flaw, or potential runtime error.\n"
            "Explain what the error is and why it occurs, but do not provide the corrected code yet.\n"
        ),
        "Number of Errors": (
            f"Analyze the following {language} code and count the exact number of errors.\n"
            "Provide a bulleted list enumerating each error found (e.g., 1. Syntax error on line X...). "
            "At the top, boldly state 'Total Errors Found: N'.\n"
        ),
        "Error Correction": (
            f"Analyze the following {language} code, detect all errors, and correct them.\n"
            "Provide a brief explanation of what was wrong, and then provide the fully corrected and working code.\n"
            f"CRITICAL: Output the corrected code inside a single standard ```{language.lower()} code block so it can be extracted and executed.\n"
        ),
        "Simple Code": (
            f"Analyze the following {language} code and rewrite it to be as simple, clean, and readable as possible.\n"
            "Remove unnecessary complexity, use better variable names, and follow best practices.\n"
            f"CRITICAL: Output the simplified code inside a single standard ```{language.lower()} code block so it can be extracted and executed.\n"
        ),
        "Comprehensive Review": (
            f"Perform a comprehensive review of the following {language} code including bug detection, optimization, and best practices.\n"
            "Present your response clearly structured with:\n"
            "- Identified Issues\n"
            "- Explanations\n"
            f"- The fully corrected and optimized code inside a single standard ```{language.lower()} code block.\n"
        )
    }

    base_prompt = prompts.get(analysis_type, prompts["Comprehensive Review"])
    
    full_prompt = f"{base_prompt}\n\nHere is the code to analyze:\n\n```{language}\n{code}\n```"

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                 temperature=0.2, # Lower temperature for more analytical/factual code review
            )
        )
        return response.text
    except Exception as e:
        return f"An error occurred during analysis: {e}"

