# This file makes Python treat the directory as a package.
# Import only the DynaPyt analyzer to avoid circular imports
try:
    from .dynapyt_analyzer import run_dynapyt_analysis, DynaPytAnalyzer, DYNAPYT_AVAILABLE
except ImportError:
    # Fallback if DynaPyt is not available
    def run_dynapyt_analysis(*args, **kwargs):
        return {"error": "DynaPyt not available"}
    
    class DynaPytAnalyzer:
        def __init__(self):
            self.available = False
    
    DYNAPYT_AVAILABLE = False

__all__ = [
    'run_dynapyt_analysis',
    'DynaPytAnalyzer', 
    'DYNAPYT_AVAILABLE'
]
