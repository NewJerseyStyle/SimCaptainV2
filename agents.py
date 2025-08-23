import os
import json
from typing import Any, Dict, List, Optional, Tuple, Union

import fastapi_poe as fp
from fastapi_poe.types import ProtocolMessage

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration # Import ChatResult and ChatGeneration
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool, Tool

class PoeChatModel(BaseChatModel):
    """
    A custom LangChain ChatModel wrapper for fastapi_poe.
    This allows LangChain/Langgraph agents to use Poe bots as their LLM.
    """
    bot_name: str
    api_key: str
    _bound_tools: List[BaseTool] = []

    def __init__(self, bot_name: str, api_key: str, **kwargs: Any):
        super().__init__(bot_name=bot_name, api_key=api_key, **kwargs)
        if not self.api_key:
            raise ValueError("POE_API_KEY environment variable not set.")

    def _format_tools_for_prompt(self) -> str:
        """Formats the bound tools into a string suitable for injecting into the prompt."""
        if not self._bound_tools:
            return ""
        tool_strings = []
        for tool_obj in self._bound_tools:
            tool_strings.append(f"Tool Name: {tool_obj.name}\nDescription: {tool_obj.description}\nArgs: {tool_obj.args}")
        return "\n\nAvailable Tools:\n" + "\n---\n".join(tool_strings) + "\n---\n"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        poe_messages = []
        tool_definitions = self._format_tools_for_prompt()

        # Prepend tool definitions to the first user message or system message
        if tool_definitions:
            if messages and isinstance(messages[0], SystemMessage):
                messages[0].content = tool_definitions + "\n" + messages[0].content
            elif messages and isinstance(messages[0], HumanMessage):
                messages[0].content = tool_definitions + "\n" + messages[0].content
            else:
                # If no initial message, create a system message with tools
                poe_messages.append(ProtocolMessage(role="user", content=tool_definitions))


        for msg in messages:
            if isinstance(msg, HumanMessage):
                poe_messages.append(ProtocolMessage(role="user", content=msg.content))
            elif isinstance(msg, AIMessage):
                poe_messages.append(ProtocolMessage(role="bot", content=msg.content))
            elif isinstance(msg, SystemMessage):
                poe_messages.append(ProtocolMessage(role="user", content=f"System instruction: {msg.content}"))
            else:
                poe_messages.append(ProtocolMessage(role="user", content=msg.content)) # Fallback

        full_response_content = ""
        try:
            for partial_response in fp.get_bot_response_sync(
                messages=poe_messages,
                bot_name=self.bot_name,
                api_key=self.api_key,
                # You can pass other parameters like temperature, top_p if Poe API supports them
                # model=kwargs.get("model", "default_poe_model"),
            ):
                full_response_content += partial_response.text
            
            # LangChain expects a ChatResult object, which contains a list of ChatGeneration objects.
            ai_message = AIMessage(content=full_response_content)
            return ChatResult(generations=[ChatGeneration(text=full_response_content, message=ai_message)])
        except Exception as e:
            print(f"Error calling Poe LLM for {self.bot_name}: {e}")
            raise e # Re-raise to be caught by langgraph

    @property
    def _llm_type(self) -> str:
        return "poe_chat_model"

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        # Implement streaming if needed, similar to _generate but yielding chunks
        raise NotImplementedError("PoeChatModel does not support streaming yet.")

    def get_num_tokens(self, text: str) -> int:
        # Placeholder for token counting
        return len(text.split())

    def bind_tools(self, tools: List[Union[Dict[str, Any], BaseTool]], **kwargs: Any) -> Runnable[List[BaseMessage], BaseMessage]:
        """Bind tools to the model. Returns a new model with tools bound."""
        # Create a new instance of PoeChatModel, passing necessary init args
        new_model = self.__class__(bot_name=self.bot_name, api_key=self.api_key)
        new_model._bound_tools = [Tool.from_function(t) if isinstance(t, dict) else t for t in tools]
        return new_model
