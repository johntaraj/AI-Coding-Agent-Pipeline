# pip install langgraph-codeact "langchain[anthropic]"
import asyncio
import inspect
import uuid
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_sandbox import PyodideSandbox

from langgraph_codeact import EvalCoroutine, create_codeact

import os 
# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Get the project root directory (assuming this file is in src/analysis/dynamic_analyzer/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..', '..')
    env_path = os.path.join(project_root, 'config', '.env')
    load_dotenv(dotenv_path=env_path)
    print(f"Loading environment variables from: {env_path}")
except ImportError:
    print("Warning: python-dotenv not available. Install with: pip install python-dotenv")



def create_pyodide_eval_fn(sandbox: PyodideSandbox) -> EvalCoroutine:
    """Create an eval_fn that uses PyodideSandbox.
    """

    async def async_eval_fn(
        code: str, _locals: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        # Create a wrapper function that will execute the code and return locals
        wrapper_code = f"""
def execute():
    try:
        # Execute the provided code
{chr(10).join("        " + line for line in code.strip().split(chr(10)))}
        return locals()
    except Exception as e:
        return {{"error": str(e)}}

execute()
"""
        # Convert functions in _locals to their string representation
        context_setup = ""
        for key, value in _locals.items():
            if callable(value):
                # Get the function's source code
                src = inspect.getsource(value)
                context_setup += f"\n{src}"
            else:
                context_setup += f"\n{key} = {repr(value)}"

        ## add dynapyt code


        
        try:
            # Execute the code and get the result
            response = await sandbox.execute(
                code=context_setup + "\n\n" + wrapper_code,
            )

            # Check if execution was successful
            if response.stderr:
                return f"Error during execution: {response.stderr}", {}

            # Get the output from stdout
            output = (
                response.stdout
                if response.stdout
                else "<Code ran, no output printed to stdout>"
            )
            result = response.result

            # If there was an error in the result, return it
            if isinstance(result, dict) and "error" in result:
                return f"Error during execution: {result['error']}", {}

            # Get the new variables by comparing with original locals
            new_vars = {
                k: v
                for k, v in result.items()
                if k not in _locals and not k.startswith("_")
            }
            return output, new_vars

        except Exception as e:
            return f"Error during PyodideSandbox execution: {repr(e)}", {}

    return async_eval_fn


def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    return a / b


def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b


def sin(a: float) -> float:
    """Take the sine of a number."""
    import math

    return math.sin(a)


def cos(a: float) -> float:
    """Take the cosine of a number."""
    import math

    return math.cos(a)


def radians(a: float) -> float:
    """Convert degrees to radians."""
    import math

    return math.radians(a)


def exponentiation(a: float, b: float) -> float:
    """Raise one number to the power of another."""
    return a**b


def sqrt(a: float) -> float:
    """Take the square root of a number."""
    import math

    return math.sqrt(a)


def ceil(a: float) -> float:
    """Round a number up to the nearest integer."""
    import math

    return math.ceil(a)


tools = [
    # add,
    # multiply,
    # divide,
    # subtract,
    # sin,
    # cos,
    # radians,
    # exponentiation,
    # sqrt,
    # ceil,
]

model = init_chat_model("gpt-4o", model_provider="openai")

sandbox = PyodideSandbox(sessions_dir="./sandbox_sessions", allow_net=True)
eval_fn = create_pyodide_eval_fn(sandbox)
code_act = create_codeact(model, tools, eval_fn)
agent = code_act.compile()

query = """ calculate the area of a circle with radius 5"""


def run_agent(query: str):
    """Run the agent using invoke instead of streaming."""
    # Use invoke to get the final result directly
    result = agent.invoke(
        {"messages": query},
        config={"configurable": {"thread_id": "default"}}
    )
    
    # Print the final result
    print("=== Agent Response ===")
    print(result)
    print("\n=== Final Messages ===")
    
    # Extract and display the messages if available
    if "messages" in result:
        for i, message in enumerate(result["messages"]):
            print(f"Message {i+1}: {message}")
    
    return result


async def run_agent_async(query: str):
    """Async version using ainvoke instead of astream."""
    # Use ainvoke to get the final result directly
    result = await agent.ainvoke(
        {"messages": query},
        config={"configurable": {"thread_id": "default"}}
    )
    
    # Print the final result
    print("=== Agent Response ===")
    print(result)
    print("\n=== Final Messages ===")
    
    # Extract and display the messages if available
    if "messages" in result:
        for i, message in enumerate(result["messages"]):
            print(f"Message {i+1}: {message}")
    
    return result


if __name__ == "__main__":
    # PyodideSandbox requires async operations, so we must use the async version
    print("Running with asynchronous ainvoke...")
    asyncio.run(run_agent_async(query))
    
    # Note: Synchronous invoke doesn't work with PyodideSandbox
    # Uncomment below only if you replace PyodideSandbox with a sync alternative
    # print("Running with synchronous invoke...")
    # run_agent(query)




# result = await sandbox.execute(
#         code="""
# x = 5 + 3
# y = x * 2
# print(f"x = {x}, y = {y}")
# result = {"calculation": x, "doubled": y}
# result
# """
#     )
    
# print("STDOUT:", result.stdout)
# print("RESULT:", result.result)
# print("STDERR:", result.stderr)