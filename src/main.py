#%%
import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
#%%
# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))
#%%
# Ensure the OPENAI_API_KEY is loaded (optional: add error handling)
api_key = os.getenv("OPENAI_API_KEY")
#%%
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file.")
    exit()
#%%
llm = ChatOpenAI(openai_api_key=api_key)
#%%
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])
#%%
def extract_python_code(text: str) -> str:
    """Extracts code from a Python Markdown code block.

    Args:
        text: The raw text response from the LLM.

    Returns:
        The extracted Python code, or the original text if no block is found.
    """
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback or handle cases where no code block is found
    print("Warning: No Python code block found in the response.") 
    # Decide on fallback: return original text, empty string, or raise error?
    # Returning original text for now, but might need adjustment.
    return text # Or return "" or raise ValueError("No Python code block found")

output_parser = StrOutputParser()
codeparser = RunnableLambda(extract_python_code)

chain = prompt | llm | output_parser | codeparser
#%%
input_text = "generate a python code to print hello world"
print(f"Invoking chain with input: '{input_text}'")
response = chain.invoke({"input": input_text})

print("\nResponse:")
print(response)

# %%

from openevals.code.pyright import create_pyright_evaluator

evaluator = create_pyright_evaluator()

response = "print('Hello, World!')" 

result = evaluator(outputs=response)

print(result)

# %%