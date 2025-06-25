import re
from typing import Optional

def extract_python_code(llm_response: str) -> Optional[str]:
    """
    Extracts Python code from the LLM's response.
    It looks for code enclosed in ```python ... ``` or ``` ... ```.
    If multiple blocks are found, it returns the first one.
    If no blocks are found but the response seems to be raw code, it returns the whole response.
    """
    # Pattern to find code blocks like ```python ... ```
    python_block_pattern = re.compile(r"```python\s*(.*?)\s*```", re.DOTALL)
    # Pattern to find generic code blocks like ``` ... ```
    generic_block_pattern = re.compile(r"```\s*(.*?)\s*```", re.DOTALL)

    match = python_block_pattern.search(llm_response)
    if match:
        return match.group(1).strip()

    match = generic_block_pattern.search(llm_response)
    if match:
        return match.group(1).strip()

    # If no markdown code blocks are found, assume the entire response might be code,
    # especially if the prompt is very strict.

    # This is a fallback and might need refinement based on llm behavior.
   
    # A simple check: if it contains typical Python keywords and doesn't look like conversational text.
    # For now, if no blocks, return the whole thing if it's not too long and doesn't contain "sorry", "I can't", etc.
   
    # A simpler heuristic: if it contains 'def ' or 'import ' or 'class ' and is relatively short.
    # However, the system prompt asks for ```python ... ```, so this fallback should ideally not be needed often.

    if llm_response and not llm_response.startswith("```"): # A  very basic check
        # Check if it looks like code (e.g., contains 'def ' or 'import ' or consists of multiple lines with indentation)
        # Totally weak heuristic. The primary expectation is markdown blocks.
        lines = llm_response.strip().split('\n')
        if any(kw in llm_response for kw in ['def ', 'import ', 'class ', 'print(']) or \
           (len(lines) > 1 and any(line.startswith(' ') for line in lines)):
            return llm_response.strip()
            
    return None