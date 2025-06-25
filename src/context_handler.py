import pandas as pd
from typing import List, Any

def parse_files_to_context_string(files: List[Any]) -> str:
    """
    Parses a list of uploaded files (from Streamlit) into a single string for the LLM context.

    Args:
        files: A list of Streamlit UploadedFile objects.

    Returns:
        A formatted string containing the content of all files, or an empty string if no files.
    """
    if not files:
        return "No files were provided as context."

    context_string = ""
    for file in files:
        filename = file.name
        context_string += f"--- START OF FILE: {filename} ---\n"
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
                context_string += df.to_string() + "\n"
            elif filename.endswith('.xlsx'):
                # To read all sheets from an Excel file
                xls = pd.ExcelFile(file)
                for i, sheet_name in enumerate(xls.sheet_names):
                    if i > 0:
                        context_string += f"\n--- Content of sheet: {sheet_name} ---\n"
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    context_string += df.to_string() + "\n"
            elif filename.endswith(('.txt', '.py')):
                content = file.getvalue().decode("utf-8")
                context_string += content + "\n"
            else:
                context_string += "Unsupported file type.\n"
        except Exception as e:
            context_string += f"Error reading file: {e}\n"
        context_string += f"--- END OF FILE: {filename} ---\n\n"
    
    return context_string

def create_initial_prompt(user_query: str, file_context: str) -> str:
    """
    Creates the initial prompt for the LLM, combining the user's query and file context.
    """
    return (
        f"A user wants to generate a Python script. Here is their request and the content of the files they provided.\n\n"
        f"**USER'S REQUEST:**\n{user_query}\n\n"
        f"**FILE CONTEXT:**\n{file_context}\n\n"
        "Based on the request and the file context, please generate the complete Python script."
    )

def create_feedback_prompt(
    original_user_query: str,
    file_context: str,
    failed_code: str,
    analysis_issues: List[str]
) -> str:
    """
    Creates a feedback prompt for the LLM when the previous code had issues.
    It includes all original context plus the errors.
    """
    issues_str = "\n- ".join(analysis_issues)
    return (
        f"The Python code you previously generated for the request had issues.\n\n"
        f"**ORIGINAL USER'S REQUEST:**\n{original_user_query}\n\n"
        f"**ORIGINAL FILE CONTEXT:**\n{file_context}\n\n"
        f"**THE FAILED CODE YOU WROTE:**\n"
        f"```python\n{failed_code}\n```\n\n"
        f"**ANALYSIS FOUND THESE ISSUES:**\n- {issues_str}\n\n"
        "Please analyze the original request, the file context, and the errors. "
        "Provide a new, corrected version of the complete Python script."
    )