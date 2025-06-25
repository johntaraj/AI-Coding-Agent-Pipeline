import tempfile
import os
from contextlib import contextmanager

# using a context manager to handle the temporary file creation and deletion better than manually to avoid resource leaks

@contextmanager
def temporary_python_file(code_content: str):
    """
    Context manager for creating and deleting a temporary Python file.
    Yields the path to the temporary file.
    """
    temp_file = None
    try:
        # Create a temporary file with a .py extension and UTF-8 ENCODING
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        )
        temp_file.write(code_content)
        temp_file.close() # Close the file so linters can open  it
        yield temp_file.name
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)