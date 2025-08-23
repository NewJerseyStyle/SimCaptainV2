import time
import json
import os
from typing import Literal, Annotated, List, TypedDict

from langchain_core.tools import tool, Tool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.managed import IsLastStep
from langchain_experimental.utilities import PythonREPL

from world import World
from ship import Ship
from agents import PoeChatModel # Custom PoeChatModel
from state_schemas import (
    BridgeState, GunneryState, TorpedoRoomState, CommunicationState,
    ShipState, EnvironmentState, TurretState, TorpedoTubeState,
    TorpedoInventory, Message, NavigationState, DamageReport,
    WeaponState, EngineState, Weather, SeaState, TargetShip, EnemyShip
)
from utils import serialize_game_state # Import serialize_game_state

class Game:
    def __init__(self, thread_id: str, world: World, player_ship: Ship, enemy_ship: Ship):
        self.world = world
        self.player_ship = player_ship
        self.enemy_ship = enemy_ship
        self.blog = [] # Global message board
        self.request = '' # For asking captain
        self.inputs = {"messages": []}
        self.thread_id = thread_id # Store thread_id for checkpointer

        # Initialize PoeChatModel
        self.poe_model = PoeChatModel(bot_name="GameMasterSC", api_key=os.getenv("POE_API_KEY"))

        @tool
        def send_bridge(role: str, message: str):
            """在艦橋上公開發言，所有人包括艦長都能知道， role 是你的身份，message 是其他人會看到的詳細信息，在其他人眼中會以 `[role]:[message]` 的格式顯示"""
            if f"{role}：" not in message[:len(role) + 2]:
                message = f"{role}：{message}"
            self.inputs["messages"].append(HumanMessage(content=message, name=role))
            return "已經寫入消息記錄，晚一些稍後會有回复"

        @tool
        def send(role: str, message: str):
            """用這個函數將 message 發送到留言板，除了玩家（船長）之外其他人都會看到它，你應該在 message 開頭表明自己的身份以及誰應該關注你提供的信息再提供信息"""
            self.blog.append(message)

        @tool
        def read_messages():
            """用這個函數獲取最新的15個留言板上的 message"""
            return '\n\n---\n\n'.join(self.blog[:15])

        @tool
        def ask_captain(role: str, message: str):
            """用這個函數將 message 發送給艦長，要求玩家（船長）做出回應"""
            self.request += role + ':\t' + message

        python_repl = PythonREPL()
        repl_tool = Tool(
            name="python_repl",
            description="A Python shell. Use this to execute python commands for your calculation in math, time, location and other simulation needs. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
            func=python_repl.run,
        )

        self.tools = [send, read_messages, send_bridge, ask_captain, repl_tool]

        # Define Langgraph agents using PoeChatModel
        # Note: checkpointer needs to be configured with a unique thread_id for each game instance
        self.sec_capt = create_react_agent(self.poe_model, tools=self.tools, state_schema=BridgeState, state_modifier=self._load_prompt("prompts/vice_captain_prompt.txt"), checkpointer=MemorySaver())
        self.bridge = create_react_agent(self.poe_model, tools=self.tools, state_schema=BridgeState, state_modifier=self._load_prompt("prompts/bridge_prompt.txt"), checkpointer=MemorySaver())
        self.guns = create_react_agent(self.poe_model, tools=self.tools, state_schema=GunneryState, state_modifier=self._load_prompt("prompts/gunnery_officer_prompt.txt"), checkpointer=MemorySaver())
        self.torpedos = create_react_agent(self.poe_model, tools=self.tools, state_schema=TorpedoRoomState, state_modifier=self._load_prompt("prompts/torpedo_officer_prompt.txt"), checkpointer=MemorySaver())
        self.navigate = create_react_agent(self.poe_model, tools=self.tools, state_schema=CommunicationState, state_modifier=self._load_prompt("prompts/navigator_prompt.txt"), checkpointer=MemorySaver())
        self.ship_agent = create_react_agent(self.poe_model, tools=self.tools, state_schema=ShipState, state_modifier=self._load_prompt("prompts/ship_damage_control_prompt.txt"), checkpointer=MemorySaver())
        self.world_agent = create_react_agent(self.poe_model, tools=self.tools, state_schema=EnvironmentState, state_modifier=self._load_prompt("prompts/environment_simulator_prompt.txt"), checkpointer=MemorySaver())

        self.actors = [
            ("副艦長", self.sec_capt),
            ("炮術長", self.guns),
            ("水雷長", self.torpedos),
            ("通信長", self.navigate),
            ("[艦橋]", self.bridge),
            ("(船艦狀態模擬器)", self.ship_agent),
            ("(環境模擬器)", self.world_agent),
        ]
        self.inputs["messages"].append(("assistant", "System: 由副艦長向所有人說明任務和艦船的狀態，確認所有人對情況、時間和艦船狀態的理解是一致的，然後等待艦長指示並通過艦長指示的語言判斷遊戲採用中文、日文還是英文進行"))
        # Removed game_intro as it will be handled by prompts
        # self.blog.append(f"系統：遊戲設定：{game_intro}")
        self.message_len = len(self.inputs["messages"])
        self.config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 25}
        self.i = 0

    def _load_prompt(self, prompt_path: str) -> str:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def turn(self, inp: str):
        res = []
        # Serialize game state and add to inputs for agents
        game_state_str = serialize_game_state(self.world, self.player_ship, self.enemy_ship)
        self.inputs["messages"].append(HumanMessage(content=f"Current Game State: {game_state_str}", name="System"))
        self.inputs["messages"].append(("user", f"艦長：{inp}"))
        self.message_len += 2 # Account for game state and user input
        
        # Update world and ship state before agent turn
        self.world.update(delta_time=0.1) # Assuming 0.1 hours per turn for now
        self.player_ship.update(delta_time=0.1)
        self.enemy_ship.update(delta_time=0.1)

        try:
            for s in self.actors[self.i][1].stream(self.inputs, self.config, stream_mode="values"):
                message = s["messages"][-1]
                # if isinstance(message, tuple):
                #     print(message)
                # else:
                #     message.pretty_print()
        except Exception as e:
            print(f"Error during agent turn for {self.actors[self.i][0]}: {e}")
            pass # Continue to next agent even if one fails

        if self.message_len != len(self.inputs["messages"]):
            for m in self.inputs["messages"][self.message_len:]:
                if isinstance(m, tuple):
                    role, content = m
                else:
                    role = m.name
                    content = m.content
                content = '\n'.join([l for l in content.split('\n') if len(l) == 0 or '>' != l[0]])
                res.append({"id": self.i, "role": role, "content": content, "continue": True})
        self.message_len = len(self.inputs["messages"])
        if len(self.request):
            res.append({"id": self.i, "role": self.actors[self.i][0], "content": self.request, "continue": False})
            self.request = ''
        self.i = (self.i + 1) % len(self.actors)
        if self.i == 0:
            if len(res) == 0:
                res.append({"id": 0, "role": "System", "content": "Press enter", "continue": False})
            res[-1]["continue"] = False
        return res