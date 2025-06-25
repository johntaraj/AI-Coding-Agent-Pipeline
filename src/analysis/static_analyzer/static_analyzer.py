import subprocess
import json
import sys
import os
from typing import List

# Add the project root to Python path to enable imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils import temporary_python_file

def run_pylint(code_string: str) -> List[str]:
    """
    Runs Pylint on the given Python code string and returns a list of issues.
    Focuses on Errors (E), Warnings (W), and Fatal (F) messages.
    """
    issues = []
    try:
        with temporary_python_file(code_string) as filepath:
            # Using a message template for consistent, parsable output.
            # Disabling all messages first, then enabling specific categories (E, W, F).
            msg_template = "{path}:{line}:{column}: [{msg_id}({symbol})] {msg}"
            command = [
                'pylint', filepath,
                '--output-format=text',
                f'--msg-template={msg_template}',
                '--disable=all',
                '--enable=E,W,F' # Errors, Warnings, Fatal
            ]
            process = subprocess.run(command, capture_output=True, text=True, check=False)
            
            output_lines = process.stdout.strip().split('\n')
            # Filter out empty lines or lines that are not actual issues (headers/footers might be added depending on Pylint version/config)
            for line in output_lines:
                if line.strip() and ":" in line and "[" in line and "]" in line: # Heuristic for issue lines
                    # Removing the temporary file path prefix for cleaner messages
                    issues.append(line.replace(f"{filepath}:", "line ", 1))
            
            if not issues and process.returncode != 0 and process.stdout.strip():
                # If Pylint reported issues (non-zero exit code) but we couldn't parse specific messages,
                # provide a generic message with some output.
                issues.append(f"Pylint indicated issues (exit code {process.returncode}), but no specific messages were parsed. Raw output snippet: {process.stdout.strip()[:200]}...")

    except FileNotFoundError:
        issues.append("Pylint not found. Please ensure it's installed and in your system's PATH.")
    except Exception as e:
        issues.append(f"An error occurred while running Pylint: {str(e)}")
    return issues

def run_bandit(code_string: str) -> List[str]:
    """
    Runs Bandit on the given Python code string and returns a list of security issues.
    """
    issues = []
    try:
        with temporary_python_file(code_string) as filepath:
            command = ['bandit', '-r', filepath, '-f', 'json']
            process = subprocess.run(command, capture_output=True, text=True, check=False)

            # Bandit exits with 0 if no issues, 1 if issues are found.
            # Other exit codes might indicate errors.
            if process.returncode in [0, 1]:
                try:
                    report = json.loads(process.stdout)
                    for result in report.get('results', []):
                        issue_text = (
                            f"Bandit: [{result['issue_severity']}/{result['issue_confidence']}] "
                            f"{result['issue_text']} (ID: {result['test_id']}, Line: {result['line_number']})"
                        )
                        issues.append(issue_text)
                except json.JSONDecodeError:
                    if process.stdout.strip(): # If  there's output but not JSON
                        issues.append(f"Bandit: Error parsing JSON report. Raw output: {process.stdout.strip()[:200]}...")
                    elif process.returncode == 1: # Issues found but no parseable output
                        issues.append("Bandit: Issues found, but report format was unexpected.")
            else:
                error_message = f"Bandit: Error during scan (exit code {process.returncode})."
                if process.stderr:
                    error_message += f" Stderr: {process.stderr.strip()[:200]}..."
                issues.append(error_message)

    except FileNotFoundError:
        issues.append("Bandit not found. Please ensure it's installed and in your system's PATH.")
    except Exception as e:
        issues.append(f"An error occurred while running Bandit: {str(e)}")
    return issues


def run_mypy(code_string: str) -> List[str]:
    """
    Runs MyPy on the given Python code string and returns a list of type checking issues.
    """
    issues = []
    try:
        with temporary_python_file(code_string) as filepath:
            command = [
                'mypy', filepath,
                '--show-error-codes',
                '--show-column-numbers', 
                '--no-color-output'
            ]
            
            process = subprocess.run(command, capture_output=True, text=True, check=False)
            
            output_lines = process.stdout.strip().split('\n')
            for line in output_lines:
                if line.strip() and ":" in line and "error:" in line:
                    issues.append(line.replace(f"{filepath}:", "line ", 1))
            
            if not issues and process.returncode != 0 and process.stdout.strip():
                issues.append(f"MyPy indicated issues (exit code {process.returncode}), but no specific messages were parsed.")

    except FileNotFoundError:
        issues.append("MyPy not found. Please ensure it's installed and in your system's PATH.")
    except Exception as e:
        issues.append(f"An error occurred while running MyPy: {str(e)}")
    
    return issues
