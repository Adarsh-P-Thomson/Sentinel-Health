"""
LLM Configuration and Initialization
Handles Azure OpenAI and standard OpenAI setup
"""
from typing import Optional
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from app.core.config import settings


def get_llm(
    temperature: float = 0.0,
    model: Optional[str] = None,
    streaming: bool = False
) -> BaseChatModel:
    """
    Get configured LLM instance (Azure OpenAI or standard OpenAI)
    
    Args:
        temperature: Temperature for generation (0.0 = deterministic, 1.0 = creative)
        model: Model name override (optional)
        streaming: Enable streaming responses
        
    Returns:
        BaseChatModel: Configured LLM instance
        
    Raises:
        ValueError: If no API keys are configured
    """
    # Priority 1: Azure OpenAI
    if settings.azure_openai_api_key and settings.azure_openai_endpoint:
        print(f"🤖 Using Azure OpenAI: {settings.azure_openai_deployment_name}")
        return AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=model or settings.azure_openai_deployment_name,
            temperature=temperature,
            streaming=streaming,
        )
    
    # Priority 2: Standard OpenAI
    elif settings.openai_api_key:
        print(f"🤖 Using OpenAI: {model or 'gpt-4'}")
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=model or "gpt-4",
            temperature=temperature,
            streaming=streaming,
        )
    
    # Priority 3: Groq (fallback)
    elif settings.groq_api_key:
        from langchain_groq import ChatGroq
        print(f"🤖 Using Groq: {model or 'llama3-70b-8192'}")
        return ChatGroq(
            api_key=settings.groq_api_key,
            model_name=model or "llama3-70b-8192",
            temperature=temperature,
        )
    
    else:
        raise ValueError(
            "No LLM API key configured. Please set one of:\n"
            "  - AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT\n"
            "  - OPENAI_API_KEY\n"
            "  - GROQ_API_KEY"
        )


def get_structured_llm(schema, **kwargs) -> BaseChatModel:
    """
    Get LLM configured for structured output
    
    Args:
        schema: Pydantic model for structured output
        **kwargs: Additional arguments for get_llm()
        
    Returns:
        BaseChatModel: LLM with structured output
    """
    llm = get_llm(**kwargs)
    return llm.with_structured_output(schema)
