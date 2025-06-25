#%%
"""
Dynamic Analysis Framework Main Module

This module serves as the main entry point for dynamic analysis tools,
currently supporting DynaPyt with space for future CodeAct integration.

Available Analyzers:
- DynaPyt: Runtime analysis and instrumentation for Python code
- CodeAct: [Future] Multi-language dynamic analysis framework
"""

from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# DynaPyt Integration
try:
    # Try relative import first (when run as module)
    from .dynapyt_analyzer import DynaPytAnalyzer, run_dynapyt_analysis
except ImportError:
    # Fallback to absolute import (when run directly)
    from dynapyt_analyzer import DynaPytAnalyzer, run_dynapyt_analysis

# CodeAct Integration - Future Implementation
# TODO: Add CodeAct integration when available
# try:
#     from .codeact_analyzer import CodeActAnalyzer, run_codeact_analysis
# except ImportError:
#     from codeact_analyzer import CodeActAnalyzer, run_codeact_analysis


class DynamicAnalysisFramework:
    """
    Main framework for coordinating dynamic analysis tools.
    
    Currently supports:
    - DynaPyt for Python runtime analysis
    
    Future support planned for:
    - CodeAct for multi-language dynamic analysis
    """
    
    def __init__(self):
        """Initialize the dynamic analysis framework."""
        self.dynapyt_analyzer = DynaPytAnalyzer()
        # TODO: Initialize CodeAct analyzer when available
        # self.codeact_analyzer = CodeActAnalyzer()
        
    def get_available_analyzers(self) -> List[str]:
        """Get list of available analyzers."""
        analyzers = []
        
        # Check DynaPyt availability
        if self.dynapyt_analyzer.is_available():
            analyzers.append("dynapyt")
            
        # TODO: Check CodeAct availability when implemented
        # if hasattr(self, 'codeact_analyzer') and self.codeact_analyzer.is_available():
        #     analyzers.append("codeact")
            
        return analyzers
        
    def run_analysis(
        self, 
        code: str, 
        analyzer: str = "dynapyt", 
        analysis_type: str = "comprehensive",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run dynamic analysis using the specified analyzer.
        
        Args:
            code: Source code to analyze
            analyzer: Analyzer to use ("dynapyt" or "codeact")
            analysis_type: Type of analysis to perform
            **kwargs: Additional analyzer-specific arguments
            
        Returns:
            Analysis results dictionary
        """
        if analyzer == "dynapyt":
            return self._run_dynapyt_analysis(code, analysis_type, **kwargs)
        elif analyzer == "codeact":
            return self._run_codeact_analysis(code, analysis_type, **kwargs)
        else:
            raise ValueError(f"Unknown analyzer: {analyzer}")
    
    def _run_dynapyt_analysis(
        self, 
        code: str, 
        analysis_type: str = "comprehensive",
        **kwargs
    ) -> Dict[str, Any]:
        """Run DynaPyt analysis."""
        if not self.dynapyt_analyzer.is_available():
            return {
                "error": "DynaPyt not available",
                "suggestion": "Install with: pip install dynapyt"
            }
            
        return run_dynapyt_analysis(code, analysis_type, **kwargs)
    
    def _run_codeact_analysis(
        self, 
        code: str, 
        analysis_type: str = "comprehensive",
        **kwargs
    ) -> Dict[str, Any]:
        """Run CodeAct analysis - Future Implementation."""
        # TODO: Implement CodeAct integration
        return {
            "error": "CodeAct analyzer not yet implemented",
            "suggestion": "Use DynaPyt analyzer for now",
            "planned_features": [
                "Multi-language support",
                "Advanced control flow analysis",
                "Cross-language vulnerability detection",
                "Performance profiling"
            ]
        }


def run_dynamic_analysis(
    code: str,
    analyzer: str = "dynapyt",
    analysis_type: str = "comprehensive",
    **kwargs
) -> List[str]:
    """
    Convenience function to run dynamic analysis and return issues list.
    
    Args:
        code: Source code to analyze
        analyzer: Analyzer to use ("dynapyt" or "codeact")
        analysis_type: Type of analysis to perform
        **kwargs: Additional analyzer-specific arguments
        
    Returns:
        List of issue strings (compatible with pylint/bandit format)
    """
    framework = DynamicAnalysisFramework()
    results = framework.run_analysis(code, analyzer, analysis_type, **kwargs)
    
    # Convert analysis results to list of issue strings
    issues = []
    
    if "error" in results:
        issues.append(f"Dynamic Analysis Error: {results['error']}")
        return issues
    
    # Extract issues from DynaPyt results
    dynapyt_results = results.get("dynapyt_results", {})
    
    # Security issues from taint analysis
    if "SecurityTaint" in dynapyt_results:
        security_data = dynapyt_results["SecurityTaint"]
        security_risks = security_data.get("security_risks", [])
        risk_level = security_data.get("risk_level", "UNKNOWN")
        
        for risk in security_risks:
            if risk != "No immediate security risks detected":
                issues.append(f"Dynamic Analysis [{risk_level}]: {risk}")
    
    # Branch coverage issues
    if "BranchCoverage" in dynapyt_results:
        branch_data = dynapyt_results["BranchCoverage"]
        uncovered = branch_data.get("uncovered_branches", 0)
        coverage_pct = branch_data.get("coverage_percentage", 0)
        
        if uncovered > 0:
            issues.append(f"Dynamic Analysis [INFO]: {uncovered} uncovered branches detected ({coverage_pct:.1f}% coverage)")
    
    # General recommendations as informational issues
    recommendations = results.get("recommendations", [])
    for rec in recommendations:
        if "No specific recommendations" not in rec:
            issues.append(f"Dynamic Analysis [RECOMMENDATION]: {rec}")
    
    return issues


def run_dynamic_analysis_full(
    code: str,
    analyzer: str = "dynapyt", 
    analysis_type: str = "comprehensive",
    **kwargs
) -> Dict[str, Any]:
    """
    Run dynamic analysis and return full results dictionary.
    
    Args:
        code: Source code to analyze
        analyzer: Analyzer to use ("dynapyt" or "codeact")
        analysis_type: Type of analysis to perform
        **kwargs: Additional analyzer-specific arguments
        
    Returns:
        Complete analysis results dictionary
    """
    framework = DynamicAnalysisFramework()
    return framework.run_analysis(code, analyzer, analysis_type, **kwargs)

#%%
def main():
    """Main entry point for dynamic analysis CLI."""
    if len(sys.argv) < 2:
        print("Dynamic Analysis Framework")
        print("=" * 50)
        
        framework = DynamicAnalysisFramework()
        available = framework.get_available_analyzers()
        
        print(f"Available analyzers: {', '.join(available) if available else 'None'}")
        print("\nUsage: python -m src.analysis.dynamic_analyzer.dynamic_analyzer_main <file_path>")
        print("\nExample analysis using DynaPyt:")
        
        # Example code
        sample_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
'''
        
        print("\nRunning sample analysis...")
        results = run_dynamic_analysis_full(sample_code, "dynapyt", "comprehensive")
        
        if "error" not in results:
            print(results.get("summary", "Analysis completed"))
        else:
            print(f"Error: {results['error']}")
            
        return
    
    # Analyze file
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File {file_path} not found")
        return
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        print(f"Analyzing {file_path}...")
        results = run_dynamic_analysis_full(code, "dynapyt", "comprehensive")
        
        if "error" not in results:
            print(results.get("summary", "Analysis completed"))
            
            if results.get("recommendations"):
                print("\nRecommendations:")
                for rec in results["recommendations"]:
                    print(f"  - {rec}")
        else:
            print(f"Error: {results['error']}")
            
    except Exception as e:
        print(f"Error analyzing file: {e}")


if __name__ == "__main__":
    main()
