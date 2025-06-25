from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Optional

SYSTEM_PROMPT_TEMPLATE = (
    "You are an assistant that exclusively provides Python code. "
    "Given a request, you must generate the corresponding Python code. "
    "Output ONLY the Python code block, enclosed in ```python\n...\n```. "
    "Do not include any other text, explanations, or conversational elements before or after the code block. "
    "Ensure the code is complete and directly usable."
)

def get_llm_response(
    user_query: str,
    model_name: str,
    openai_api_key: Optional[str] = None,
    google_api_key: Optional[str] = None,
    temperature: float = 0.2, # Lower temperature for more deterministic code (we can experiment with 0.05 to 0.3)
    max_tokens: int = 2000
) -> str:
    """
    Gets a response from the specified LLM.

    Args:
        user_query (str): The user's query or the feedback prompt.
        model_name (str): "gpt-4o-mini" or "gemini-1.5-flash-latest".
        openai_api_key (Optional[str]): OpenAI API key.
        google_api_key (Optional[str]): Google API key.
        temperature (float): Sampling temperature for the LLM.
        max_tokens (int): Max tokens for the LLM response.

    Returns:
        str: The LLM's response content.
    """
    try:
        if model_name == "gpt-4o-mini":
            if not openai_api_key:
                return "Error: OpenAI API Key not provided."
            llm = ChatOpenAI(
                model_name="gpt-4o-mini",
                api_key=openai_api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif model_name == "gpt-3.5-turbo":
            if not openai_api_key:
                return "Error: OpenAI API Key not provided."
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                api_key=openai_api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )

        elif model_name == "gemini-1.5-flash-latest":
            if not google_api_key:
                return "Error: Google API Key not provided."
            llm = ChatGoogleGenerativeAI(
                model="models/gemini-1.5-flash-latest",
                google_api_key=google_api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        elif model_name == "gemini-2.0-flash":
            if not google_api_key:
                return "Error: Google API Key not provided."
            llm = ChatGoogleGenerativeAI(
                model="models/gemini-2.0-flash",
                google_api_key=google_api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

        else:
            return f"Error: Unsupported model '{model_name}'."

        messages = [
            SystemMessage(content=SYSTEM_PROMPT_TEMPLATE),
            HumanMessage(content=user_query),
        ]
        
        response = llm.invoke(messages)
        return response.content
    
    except Exception as e:
        # Catch potential API errors, configuration issues,  etc.
        return f"Error during LLM call: {str(e)}"
