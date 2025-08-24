import abc
import os
import json
import re
import sys
from json_repair import repair_json
from litellm import completion
import litellm

class Agent(abc.ABC):
    """
    An abstract base class for all agents in the naval simulation.
    Defines a common interface for agent behavior.
    """
    @abc.abstractmethod
    def process_command(self, command: str, game_state: dict):
        """
        Processes a given command based on the current game state.
        This method should be implemented by concrete agent classes.
        """
        pass

class CommanderAgent(Agent):
    """
    Represents a Commander agent, either the player's or an AI commander.
    Its primary role is to delegate tasks to appropriate officer agents.
    """
    def __init__(self, name: str):
        self.name = name
        self.officer_agents = {} # To store references to officer agents

    def process_command(self, command: str, game_state: dict):
        """
        Processes a high-level command and delegates it to the appropriate
        officer agent. For now, this is a placeholder.
        """
        print(f"Commander {self.name} received command: {command}")
        # In a real implementation, this would involve parsing the command
        # and calling the appropriate officer agent's method.
        # Example: if "fire" in command: self.officer_agents["WeaponsOfficer"].process_command(...)
        pass

    def add_officer(self, officer_name: str, officer_agent):
        """Adds an officer agent to the commander's delegation list."""
        self.officer_agents[officer_name] = officer_agent

def test_llm_connection(model: str) -> bool:
    """
    Test connection to the LLM provider before initializing agents.
    Returns True if connection successful, False otherwise.
    """
    print(f"Testing connection to LLM model: {model}")
    
    try:
        # Configure API keys and base URLs for different providers
        if "gpt" in model or "openai" in model:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("ERROR: OPENAI_API_KEY environment variable not set for OpenAI models.")
                return False
        elif "claude" in model or "anthropic" in model:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("ERROR: ANTHROPIC_API_KEY environment variable not set for Anthropic models.")
                return False
        elif "ollama" in model:
            # For local Ollama models, set the base URL
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            litellm.api_base = base_url
        
        # Test with a minimal request
        test_messages = [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": "Respond with just 'OK'"}
        ]
        
        response = completion(
            model=model,
            messages=test_messages,
            temperature=0,
            max_tokens=10
        )
        
        if response and response.choices:
            print(f"✓ LLM connection test successful for model: {model}")
            return True
        else:
            print(f"✗ LLM connection test failed - no response from model: {model}")
            return False
            
    except Exception as e:
        print(f"✗ LLM connection test failed for model {model}: {e}")
        return False

class OfficerAgent(Agent, abc.ABC):
    """
    A base class for different officer roles (e.g., Weapons, Helm, Engineering).
    Responsible for receiving commands, preparing prompts, interacting with LLM,
    and parsing responses.
    """
    def __init__(self, bot_name: str, prompt_path: str, model: str = None):
        self.bot_name = bot_name
        self.prompt_path = prompt_path
        
        # Configure LLM provider and model
        self.model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        
        # Set up litellm configuration
        litellm.set_verbose = os.getenv("LLM_DEBUG", "false").lower() == "true"
        
        # Configure API keys for different providers
        if "gpt" in self.model or "openai" in self.model:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set for OpenAI models.")
        elif "claude" in self.model or "anthropic" in self.model:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set for Anthropic models.")
        elif "ollama" in self.model:
            # For local Ollama models, set the base URL
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            litellm.api_base = base_url
        # Add more provider configurations as needed

    def _prepare_prompt(self, commander_order: str, game_state: dict) -> str:
        """
        Prepares the prompt for the LLM by injecting commander order and game state.
        """
        with open(self.prompt_path, 'r') as f:
            prompt_template = f.read()
        
        return prompt_template.format(
            bot_name=self.bot_name,
            commander_order=commander_order,
            game_state=game_state
        )

    def _call_llm(self, prompt: str) -> dict:
        """
        Calls the LLM and gets a JSON response using litellm.
        """
        print(f"Calling LLM ({self.model}) for {self.bot_name} with prompt: {prompt[:100]}...")
        
        messages = [
            {"role": "system", "content": f"You are {self.bot_name}, a naval officer. Always respond with valid JSON as specified in the prompt."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            full_response_content = response.choices[0].message.content
            print(f"LLM Response for {self.bot_name}: {full_response_content[:200]}...")
            return {"action": "llm_response", "parameters": {"response": full_response_content}}
            
        except Exception as e:
            print(f"Error calling LLM ({self.model}) for {self.bot_name}: {e}")
            return {"action": "error", "parameters": {"message": str(e)}}

    def _parse_llm_response(self, response: dict):
        """
        Parses the JSON response from the LLM.
        For AICommander, it returns the full JSON dictionary.
        For other officers, it returns an (action, parameters) tuple.
        """
        if response.get("action") != "llm_response":
            if self.bot_name == "AICommander":
                return None
            return response.get("action"), response.get("parameters", {})

        llm_output = response.get("parameters", {}).get("response", "")
        
        json_str = ""
        # Extract JSON from markdown code block
        match = re.search(r"```json\s*(.*?)\s*```", llm_output, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # If no markdown, assume the whole output is JSON or contains JSON
            # Find the first '{' and last '}'
            start = llm_output.find('{')
            end = llm_output.rfind('}')
            if start != -1 and end != -1:
                json_str = llm_output[start:end+1]
            else:
                json_str = llm_output

        if not json_str:
             print(f"Could not find JSON in LLM response for {self.bot_name}: '{llm_output}'")
             if self.bot_name == "AICommander":
                return None
             return None, None

        try:
            parsed_json = json.loads(repair_json(json_str))
            
            if self.bot_name == "AICommander":
                return parsed_json
            else:
                action = parsed_json.get("action")
                parameters = parsed_json.get("parameters", {})
                return action, parameters

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response for {self.bot_name}: '{json_str}'. Error: {e}")
            if self.bot_name == "AICommander":
                return None
            else:
                return None, None

    def process_command(self, commander_order: str, game_state: dict):
        """
        Receives a command from the commander, prepares the prompt,
        calls the LLM, and parses the response.
        """
        prompt = self._prepare_prompt(commander_order, game_state)
        llm_response = self._call_llm(prompt)
        if self.bot_name == "AICommander":
            # For AICommander, the response is the full JSON dictionary
            parsed_json = self._parse_llm_response(llm_response)
            print(f"{self.bot_name} received order: '{commander_order}'. Formulated plan: {parsed_json}")
            return parsed_json
        else:
            # For other officers, it's an (action, parameters) tuple
            action, parameters = self._parse_llm_response(llm_response)
            print(f"{self.bot_name} received order: '{commander_order}'. Decided action: {action} with params: {parameters}")
            return action, parameters

class WeaponsOfficerAgent(OfficerAgent):
    """
    Concrete implementation for the Weapons Officer.
    Manages the ship's offensive arsenal.
    """
    def __init__(self, model: str = None):
        super().__init__(bot_name="WeaponsOfficer", prompt_path="prompts/weapons_officer_prompt.txt", model=model)

class HelmOfficerAgent(OfficerAgent):
    """
    Concrete implementation for the Helm Officer.
    Controls the ship's movement and navigation.
    """
    def __init__(self, model: str = None):
        super().__init__(bot_name="HelmOfficer", prompt_path="prompts/helm_officer_prompt.txt", model=model)

class EngineeringOfficerAgent(OfficerAgent):
    """
    Concrete implementation for the Engineering Officer.
    Manages the ship's propulsion and power systems.
    """
    def __init__(self, model: str = None):
        super().__init__(bot_name="EngineeringOfficer", prompt_path="prompts/engineering_officer_prompt.txt", model=model)
