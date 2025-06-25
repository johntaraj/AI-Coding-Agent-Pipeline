"""
CodeAct Wrapper for Dynamic Analysis

This module provides a wrapper around the CodeAct functionality to integrate it
with the dynamic analysis framework.
"""

import asyncio
import sys
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import traceback

# Add project root to path for imports
_current_file_directory = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_current_file_directory, '..', '..', '..'))

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from src.analysis.dynamic_analyzer.codeact import (
        model, sandbox, eval_fn, code_act, agent, create_pyodide_eval_fn
    )
    CODEACT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: CodeAct not available: {e}")
    CODEACT_AVAILABLE = False
    model = None
    sandbox = None
    eval_fn = None
    code_act = None
    agent = None


@dataclass
class ExecutionResult:
    """Represents the result of executing code."""
    success: bool
    output: str
    error: str
    execution_time: float
    variables: Dict[str, Any]
    imports_used: List[str]
    functions_defined: List[str]
    security_issues: List[str]


@dataclass
class AnalysisResult:
    """Represents the complete analysis result from CodeAct."""
    analysis_summary: str
    recommendations: List[str]
    security_assessment: str
    performance_metrics: Dict[str, Any]
    execution_results: List[ExecutionResult]


def extract_imports_and_functions(code: str) -> tuple[List[str], List[str]]:
    """Extract imports and function definitions from code."""
    imports = []
    functions = []
    
    lines = code.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            imports.append(stripped)
        elif stripped.startswith('def '):
            func_name = stripped.split('(')[0].replace('def ', '').strip()
            functions.append(func_name)
    
    return imports, functions


def detect_security_issues(code: str) -> List[str]:
    """Detect potential security issues in code."""
    issues = []
    
    dangerous_functions = ['eval', 'exec', 'compile', '__import__']
    dangerous_modules = ['os.system', 'subprocess.call', 'subprocess.run']
    
    for func in dangerous_functions:
        if func in code:
            issues.append(f"Dangerous function '{func}' detected")
    
    for module in dangerous_modules:
        if module in code:
            issues.append(f"Potentially dangerous module usage '{module}' detected")
    
    if 'input(' in code:
        issues.append("User input detected - ensure proper validation")
    
    return issues


async def execute_code_with_codeact(code: str) -> ExecutionResult:
    """Execute code using CodeAct and return execution results."""
    if not CODEACT_AVAILABLE:
        return ExecutionResult(
            success=False,
            output="",
            error="CodeAct not available",
            execution_time=0.0,
            variables={},
            imports_used=[],
            functions_defined=[],
            security_issues=[]
        )
    
    start_time = time.time()
    
    try:
        # Use the CodeAct eval function to execute code
        output, new_vars = await eval_fn(code, {})
        
        execution_time = time.time() - start_time
        
        # Extract additional information
        imports, functions = extract_imports_and_functions(code)
        security_issues = detect_security_issues(code)
        
        return ExecutionResult(
            success=True,
            output=output,
            error="",
            execution_time=execution_time,
            variables=new_vars,
            imports_used=imports,
            functions_defined=functions,
            security_issues=security_issues
        )
    
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"{type(e).__name__}: {str(e)}"
        
        return ExecutionResult(
            success=False,
            output="",
            error=error_msg,
            execution_time=execution_time,
            variables={},
            imports_used=[],
            functions_defined=[],
            security_issues=detect_security_issues(code)
        )


def generate_analysis_summary(execution_results: List[ExecutionResult]) -> str:
    """Generate a summary of the analysis results."""
    if not execution_results:
        return "No execution results available"
    
    total_executions = len(execution_results)
    successful_executions = sum(1 for result in execution_results if result.success)
    total_time = sum(result.execution_time for result in execution_results)
    
    summary_parts = [
        f"Executed {total_executions} code segment(s)",
        f"Success rate: {successful_executions}/{total_executions} ({successful_executions/total_executions*100:.1f}%)",
        f"Total execution time: {total_time:.4f} seconds"
    ]
    
    if total_executions > 0:
        avg_time = total_time / total_executions
        summary_parts.append(f"Average execution time: {avg_time:.4f} seconds")
    
    # Count security issues
    total_security_issues = sum(len(result.security_issues) for result in execution_results)
    if total_security_issues > 0:
        summary_parts.append(f"Security issues detected: {total_security_issues}")
    
    return "; ".join(summary_parts)


def generate_recommendations(execution_results: List[ExecutionResult]) -> List[str]:
    """Generate recommendations based on execution results."""
    recommendations = []
    
    if not execution_results:
        return ["Unable to analyze code - no execution results"]
    
    failed_executions = [result for result in execution_results if not result.success]
    if failed_executions:
        recommendations.append(f"Fix {len(failed_executions)} failed execution(s)")
    
    # Performance recommendations
    slow_executions = [result for result in execution_results if result.execution_time > 1.0]
    if slow_executions:
        recommendations.append("Consider optimizing slow-running code segments")
    
    # Security recommendations
    security_issues = []
    for result in execution_results:
        security_issues.extend(result.security_issues)
    
    if security_issues:
        recommendations.append("Address detected security vulnerabilities")
        recommendations.append("Review usage of dangerous functions like eval() and exec()")
    
    # Function and import recommendations
    all_functions = []
    all_imports = []
    for result in execution_results:
        all_functions.extend(result.functions_defined)
        all_imports.extend(result.imports_used)
    
    if len(all_functions) > 10:
        recommendations.append("Consider organizing code into modules - many functions detected")
    
    if len(set(all_imports)) > 20:
        recommendations.append("Consider reducing number of imports for better performance")
    
    if not recommendations:
        recommendations.append("Code analysis completed successfully - no major issues detected")
    
    return recommendations


def generate_security_assessment(execution_results: List[ExecutionResult]) -> str:
    """Generate a security assessment based on execution results."""
    all_security_issues = []
    for result in execution_results:
        all_security_issues.extend(result.security_issues)
    
    if not all_security_issues:
        return "No security issues detected"
    
    unique_issues = list(set(all_security_issues))
    assessment = f"Found {len(unique_issues)} unique security issue(s): "
    assessment += "; ".join(unique_issues[:3])  # Show first 3 issues
    
    if len(unique_issues) > 3:
        assessment += f" and {len(unique_issues) - 3} more"
    
    return assessment


def calculate_performance_metrics(execution_results: List[ExecutionResult]) -> Dict[str, Any]:
    """Calculate performance metrics from execution results."""
    if not execution_results:
        return {}
    
    total_executions = len(execution_results)
    successful_executions = sum(1 for result in execution_results if result.success)
    total_time = sum(result.execution_time for result in execution_results)
    total_security_issues = sum(len(result.security_issues) for result in execution_results)
    
    metrics = {
        "total_executions": total_executions,
        "successful_executions": successful_executions,
        "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
        "total_execution_time": total_time,
        "average_execution_time": total_time / total_executions if total_executions > 0 else 0,
        "total_security_issues": total_security_issues
    }
    
    return metrics


async def run_codeact_analysis_async(code_string: str, analysis_goal: str = "Comprehensive dynamic analysis") -> AnalysisResult:
    """
    Run CodeAct analysis on the provided code.
    
    Args:
        code_string: Python code to analyze
        analysis_goal: Goal for the analysis
        
    Returns:
        AnalysisResult containing the analysis results
    """
    if not CODEACT_AVAILABLE:
        return AnalysisResult(
            analysis_summary="CodeAct not available",
            recommendations=["Install CodeAct dependencies"],
            security_assessment="Unable to assess security",
            performance_metrics={},
            execution_results=[]
        )
    
    # Split code into logical segments for analysis
    code_segments = []
    
    # For now, treat the entire code as one segment
    # In a more sophisticated implementation, we could split by functions, classes, etc.
    if code_string.strip():
        code_segments.append(code_string)
    
    # Execute each code segment
    execution_results = []
    for segment in code_segments:
        result = await execute_code_with_codeact(segment)
        execution_results.append(result)
    
    # Generate analysis components
    analysis_summary = generate_analysis_summary(execution_results)
    recommendations = generate_recommendations(execution_results)
    security_assessment = generate_security_assessment(execution_results)
    performance_metrics = calculate_performance_metrics(execution_results)
    
    return AnalysisResult(
        analysis_summary=analysis_summary,
        recommendations=recommendations,
        security_assessment=security_assessment,
        performance_metrics=performance_metrics,
        execution_results=execution_results
    )


def run_codeact_analysis(code_string: str, analysis_goal: str = "Comprehensive dynamic analysis") -> AnalysisResult:
    """
    Synchronous wrapper for CodeAct analysis.
    
    Args:
        code_string: Python code to analyze
        analysis_goal: Goal for the analysis
        
    Returns:
        AnalysisResult containing the analysis results
    """
    try:
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_codeact_analysis_async(code_string, analysis_goal))
            return result
        finally:
            loop.close()
    except Exception as e:
        # Return error result if something goes wrong
        return AnalysisResult(
            analysis_summary=f"Analysis failed: {str(e)}",
            recommendations=["Fix the error and try again"],
            security_assessment="Unable to assess security due to error",
            performance_metrics={},
            execution_results=[ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=0.0,
                variables={},
                imports_used=[],
                functions_defined=[],
                security_issues=[]
            )]
        )


def main():
    """Test the CodeAct wrapper."""
    test_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Fibonacci(10) = {result}")

# Test with potentially dangerous code
user_input = "2 + 2"
evaluated = eval(user_input)
print(f"Evaluated: {evaluated}")
'''
    
    print("Testing CodeAct Analysis Wrapper")
    print("=" * 40)
    
    result = run_codeact_analysis(test_code)
    
    print("Analysis Summary:")
    print(result.analysis_summary)
    
    print("\nRecommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")
    
    print(f"\nSecurity Assessment:")
    print(result.security_assessment)
    
    print(f"\nPerformance Metrics:")
    for key, value in result.performance_metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main() 