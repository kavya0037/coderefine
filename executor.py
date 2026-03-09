import re
import subprocess
import tempfile
import os

def extract_code_block(markdown_text: str, language: str) -> str:
    """Extracts a code block of a given language from Markdown."""
    # A simple regex to find the first block ```language\n...\n```
    # Making it case-insensitive for languages like Python/python
    pattern = rf"```{language.lower()}\n(.*?)\n```"
    match = re.search(pattern, markdown_text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def execute_code(code: str, language: str) -> str:
    """Executes the code locally using a subprocess and returns the output/errors."""
    if not code.strip():
        return "No code block found to execute."

    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "c++": ".cpp",
        "c#": ".cs",
        "go": ".go",
        "rust": ".rs"
    }
    
    lang = language.lower()
    ext = ext_map.get(lang)
    
    if not ext:
        return f"Execution for language '{language}' is not supported yet."

    # For Java, the class name often must match the file name, making generic execution tricky with a tempfile without parsing.
    # For now, we will add support for Python and Node.js which are the most straightforward.
    if lang not in ["python", "javascript"]:
        return f"Execution environment for '{language}' isn't configured in this demo (Python and JavaScript are supported)."

    with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        if lang == "python":
            cmd = ["python", temp_file_path]
        elif lang == "javascript":
            cmd = ["node", temp_file_path]
            
        # Run the command with a timeout so it doesn't hang forever
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=10 # 10 seconds timeout
        )
        
        output = result.stdout
        if result.stderr:
            output += "\n--- ERRORS ---\n" + result.stderr
            
        return output.strip() if output.strip() else "Process exited successfully with no output."
        
    except subprocess.TimeoutExpired:
        return "Execution timed out (exceeded 10 seconds)."
    except Exception as e:
        return f"Execution failed: {str(e)}"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
    
    return "Unknown execution state."
