from typing import Literal, Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.managed import IsLastStep
from langgraph.graph.message import add_messages # Import add_messages

# Base state for all agents
class BaseAgentState(TypedDict):
    role: str
    language: str
    remaining_steps: int
    messages: Annotated[list[BaseMessage], add_messages]
    is_last_step: IsLastStep

# Specific agent states
class BridgeState(BaseAgentState):
    speed: str
    direction: str
    ship_damage_condition: str
    time_now: str
    today: str
    environment: str
    situation: str
    mission: str

class TurretState(TypedDict):
    id: int
    status: str # 例如: "裝填中", "瞄準中", "射擊完畢", "故障"
    ammo_remaining: int
    opeartor_remaining: int
    elevation: int # 仰角
    azimuth: int # 方位
    malfunction_condition: str
    damaged_condition: str

class GunneryState(BaseAgentState):
    target_bearing: str # 目標方位，例如: "三點鐘方向"
    target_range: str # 目標距離，例如: "10000米"
    target_speed: str # 目標速度，例如： "20節"
    turrets: List[TurretState] # 砲塔狀態列表
    notes_about_limitation: str

class TorpedoTubeState(TypedDict):
    id: int  # 魚雷管編號：1, 2, 3
    loaded: bool  # 是否已裝填魚雷
    torpedo_type: str  # 魚雷類型，例如: "93式氧气鱼雷"
    ready: bool # 是否準備好發射

class TorpedoInventory(TypedDict):
    ready_to_load: int # 可供裝填的魚雷數量
    total: int # 總魚雷數量

class TorpedoRoomState(BaseAgentState):
    tubes: List[TorpedoTubeState] # 魚雷管狀態列表
    inventory: TorpedoInventory # 魚雷庫存
    last_reload_time: str | None # 上次重新裝填時間，例如: "0800時"，如果沒有則為 None
    notes_about_limitation: str

class Message(TypedDict):
    sender: str  # 發送者
    recipient: str  # 接收者
    content: str  # 訊息內容
    timestamp: str  # 時間戳，例如: "0800時"
    method: Literal["電報", "燈號", "聲號", "旗號", "手旗", "郵件"]  # 通訊方式

class NavigationState(TypedDict):
    current_heading: int  # 目前航向，單位：度
    current_speed: int  # 目前速度，單位：節
    target_heading: int | None  # 目標航向，單位：度，如果沒有則為 None
    target_speed: int | None  # 目標速度，單位：節，如果沒有則為 None
    position: str | None #  当前位置，例如 "34°20'N 135°15'E" 或地標名稱，如果未知則為 None

class CommunicationState(BaseAgentState):
    radio_messages: List[Message]  # 訊息列表
    navigation: NavigationState # 導航狀態

class DamageReport(TypedDict):
    location: str  # 損壞位置，例如: "前甲板"，"一號鍋爐艙"
    type: Literal["火災", "進水", "破裂", "機械故障"]  # 損壞類型
    severity: Literal["輕微", "中等", "嚴重"]  # 損壞程度
    repair_status: Literal["未開始", "進行中", "已完成"]  # 維修狀態

class WeaponState(TypedDict):
    id: int  # 武器編號，例如: 1, 2, 3
    type: Literal["主砲", "魚雷發射管"]  # 武器類型
    operational: bool  # 是否可操作

class EngineState(TypedDict):
    boiler_1: Literal["正常", "損壞", "停止"]
    boiler_2: Literal["正常", "損壞", "停止"]
    boiler_3: Literal["正常", "損壞", "停止"]
    boiler_4: Literal["正常", "損壞", "停止"]
    engine_1: Literal["正常", "損壞", "停止"]
    engine_2: Literal["正常", "損壞", "停止"]

class ShipState(BaseAgentState):
    current_speed: int
    current_heading: int
    casualties: int
    damage_reports: List[DamageReport]
    weapon_status: List[WeaponState]
    engine_state: EngineState
    fuel_level: int
    ammunition_level: int

class Weather(TypedDict):
    wind_direction: int  # 風向，單位：度，0 為正北，順時針方向
    wind_speed: int  # 風速，單位：節
    visibility: Literal["良好", "中等", "不良"]  # 能見度

class SeaState(TypedDict):
    wave_height: int
    current_direction: int  # 海流方向，單位：度，0 為正北，順時針方向
    current_speed: int  # 海流速度，單位：節

class TargetShip(TypedDict):
    name: str  # 目標船隻名稱
    latitude: float  # 緯度
    longitude: float  # 經度
    speed: int  # 速度，單位：節
    heading: int  # 航向，單位：度，0 為正北，順時針方向

class EnemyShip(TypedDict):
    name: str | None  # 敵艦名稱, 如果未知則為 None
    latitude: float | None  # 緯度, 如果未知則為 None
    longitude: float | None  # 經度, 如果未知則為 None
    speed: int | None  # 速度，單位：節, 如果未知則為 None
    heading: int | None  # 航向，單位：度，0 為正北，順時針方向, 如果未知則為 None
    type: str | None # 敵艦類型, 例如 "驅逐艦", "巡洋艦", 如果未知則為 None

class EnvironmentState(BaseAgentState):
    timestamp: str  # 時間戳，例如: "1944年6月10日03:00"
    weather: Weather  # 天氣
    sea_state: SeaState  # 海況
    target_ship: TargetShip # 目標船隻信息
    enemy_ships: List[EnemyShip]  # 敵艦列表，可以為空列表
    own_ship_latitude: float # 自身船隻緯度
    own_ship_longitude: float # 自身船隻經度