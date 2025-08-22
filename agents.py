import abc
import os
import fastapi_poe as fp
from fastapi_poe.types import ProtocolMessage
import json
import re
from json_repair import repair_json

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

class OfficerAgent(Agent, abc.ABC):
    """
    A base class for different officer roles (e.g., Weapons, Helm, Engineering).
    Responsible for receiving commands, preparing prompts, interacting with LLM,
    and parsing responses.
    """
    def __init__(self, bot_name: str, prompt_path: str):
        self.bot_name = bot_name
        self.prompt_path = prompt_path
        self.poe_api_key = os.getenv("POE_API_KEY")
        if not self.poe_api_key:
            raise ValueError("POE_API_KEY environment variable not set.")

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
        Calls the LLM and gets a JSON response using fastapi_poe.
        """
        if not self.poe_api_key:
            raise ValueError("Poe API key is not set. Cannot call LLM.")

        print(f"Calling LLM for {self.bot_name} with prompt: {prompt[:100]}...")
        messages = [ProtocolMessage(role="user", content=prompt)]
        full_response_content = ""
        try:
            for partial_response in fp.get_bot_response_sync(
                messages=messages,
                bot_name=self.bot_name,
                api_key=self.poe_api_key,
            ):
                full_response_content += partial_response.text
            return {"action": "llm_response", "parameters": {"response": full_response_content}}
        except Exception as e:
            print(f"Error calling Poe LLM for {self.bot_name}: {e}")
            # Return a default error response or re-raise the exception
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
    def __init__(self):
        super().__init__(bot_name="WeaponsOfficer", prompt_path="prompts/weapons_officer_prompt.txt")

class HelmOfficerAgent(OfficerAgent):
    """
    Concrete implementation for the Helm Officer.
    Controls the ship's movement and navigation.
    """
    def __init__(self):
        super().__init__(bot_name="HelmOfficer", prompt_path="prompts/helm_officer_prompt.txt")

class EngineeringOfficerAgent(OfficerAgent):
    """
    Concrete implementation for the Engineering Officer.
    Manages the ship's propulsion and power systems.
    """
    def __init__(self):
        super().__init__(bot_name="EngineeringOfficer", prompt_path="prompts/engineering_officer_prompt.txt")
