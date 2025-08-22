import random
from geopy.distance import distance
from geopy.point import Point
from module import Gun
from module import TorpedoLauncher
from module import EngineRoom

class Type3_127mm(Gun):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shells = 300
        self.fire_shell_cost = 2

    def is_hit(self, range):
        if range < 19:
            return random.randint(1, 6) == 6

class Torpedo_610mm_Launcher(TorpedoLauncher):
    def is_hit(self, range):
        if range < 21:
            c = random.randint(1, 3)
            if c == 1:
                return random.randint(1, 16) == 6
            if c == 2:
                return random.randint(1, 6) == 6
            if c == 3:
                return random.randint(1, 13) == 6

class Engine(EngineRoom):
    def __init__(self):
        super().__init__(
            staff_on_duty=20,
            staff_off_duty=70,
            boilers="艦本式呂號専烧鍋爐4座",
            engines="艦本式渦輪引擎（2座2軸）",
            power=50000,  # horse power
            max_speed=38,  # knot
            range_distance=5000,  # nautical miles
            cruise_speed=0,
            direction=EngineRoom.STOPPED
        )

class Channel:
    def __init__(self, name, timer):
        self.name = name
        self.messages = []
        self.new_msgs = 0
        self.timer = timer

    def send(self, role, msg):
        self.messages.append((self.timer.time, role, msg))
        self.new_msgs += 1

    def has_next(self):
        return self.new_msgs

    def get_new(self):
        return '\n'.join(
            [f'{t}\t{r}: {m}'
            for t, r, m in self.messages[:-self.new_msgs]])

    def history(self):
        msg = '\n'.join(
            [f'{t}\t{r}: {m}' for t, r, m in self.messages])
        return msg

    def over(self):
        self.new_msgs = 0

class Agent:
    def __init__(self, name, controll_tools=[], channel_tools=[], env=None):
        self.name = name
        self.state_schema = ''
        self.state_modifier = ''
        self.tools = controll_tools + channel_tools
        self.channel_tools = channel_tools
        self.env = env
    
    def event_simulator(self, time, event):
        system_prompt=f"You are the cabin {self.name.split('@')[1]} of the ship, Your current state is defined by the following parameters:\n\n{self.env}\n\nNow it is time {time}, [Event: {event}] occurs. Use tools to update some of the parameters to reflect the changes caused by the event.  Only describe the changes to the cabin's physical state. Ensure the values accurately reflect the changes caused by the event."

    def communicate_simulator(self):
        msgs = '---\n'.join([f"Channel #{c.name}\n{c.get_new()}" for c in self.channel_tools])
        if len(msgs) == 0:
            msgs = 'Phone was silent...'
        system_prompt=f"You are a friendly {self.name.split('@')[0]} in cabin {self.name.split('@')[1]}. If case you have been given order, you can use tools that operates the cabin to finish your job. The cabin is now in state:\n{self.env}\n\nFeel free to use tools to reply, some messages/orders from others:\n```\n{msgs}\n```"

    def get_status(self, message):
        system_prompt=f"You are a friendly {self.name.split('@')[0]} in cabin {self.name.split('@')[1]}. The cabin is now in state:\n{self.env}\n\nWe want your response for message: {message}"
        return None

RADIO_CHANNEL = Channel('海上公共通訊頻道')

class Fubuki:
    def __init__(self, latlong: Point):
        self.hp = 100
        self.location = latlong
        self.people_in_bridge = []
        self.actors = []
        self.bridge_speech = Channel('艦橋人員語音通訊頻道')
        self.engine_room = EngineRoom(
            staff_on_duty=20,
            staff_off_duty=70,
            boilers="艦本式呂號専烧鍋爐4座",
            engines="艦本式渦輪引擎（2座2軸）",
            power=50000,  # horse power
            max_speed=38,  # knot
            range_distance=5000,  # nautical miles
            cruise_speed=0,
            direction=EngineRoom.STOPPED
        )
        self.bridge_and_engine_message_group = Channel('艦橋-引擎通訊')
        engine_room_contact = Agent(
            '機輪長@引擎室',
            [
                self.engine_room.add_casualties,
                self.engine_room.recall_staff,
                self.engine_room.set_speed,
                self.engine_room.set_direction,
                self.engine_room.fault,
                self.engine_room.damage,
            ], [
                self.bridge_and_engine_message_group.send,
                self.bridge_and_engine_message_group.history,
            ]
        )
        self.actors.append(
            (engine_room_contact, self.bridge_and_engine_message_group))
        c_officer = Agent(
            '航海長@艦橋',
            [
                # 望遠鏡
                # 獲取輪機室情況
                # self.__str__
            ],[
                self.bridge_speech.send,
                self.bridge_speech.history,
                self.bridge_and_engine_message_group.send,
                self.bridge_and_engine_message_group.history,
            ]
        )
        self.people_in_bridge.append(c_officer)
        self.guns = [
            Type3_127mm(staff_on_duty=5, staff_off_duty=10),
            Type3_127mm(staff_on_duty=5, staff_off_duty=10),
            Type3_127mm(staff_on_duty=5, staff_off_duty=10),
        ]
        self.bridge_and_main_guns_message_group = Channel('艦橋-火砲通訊')
        main_gun_1_contact = Agent(
            '砲手@艦艏砲術室',
            [
                self.guns[0].load_ammo,
                self.guns[0].fire,
                self.guns[0].fault,
                self.guns[0].damage,
                self.guns[0].add_casualties,
                self.guns[0].recall_staff
            ], [
                self.bridge_and_main_guns_message_group.send,
                self.bridge_and_main_guns_message_group.history,
            ]
        )
        main_gun_2_contact = Agent(
            '砲手@艦尾砲術室1',
            [
                self.guns[1].load_ammo,
                self.guns[1].fire,
                self.guns[1].fault,
                self.guns[1].damage,
                self.guns[1].add_casualties,
                self.guns[1].recall_staff
            ], [
                self.bridge_and_main_guns_message_group.send,
                self.bridge_and_main_guns_message_group.history,
            ]
        )
        main_gun_3_contact = Agent(
            '砲手@艦尾砲術室2',
            [
                self.guns[2].load_ammo,
                self.guns[2].fire,
                self.guns[2].fault,
                self.guns[2].damage,
                self.guns[2].add_casualties,
                self.guns[2].recall_staff
            ], [
                self.bridge_and_main_guns_message_group.send,
                self.bridge_and_main_guns_message_group.history,
            ]
        )
        self.actors += [
            (
                main_gun_1_contact,
                self.bridge_and_main_guns_message_group
            ), (
                main_gun_2_contact,
                self.bridge_and_main_guns_message_group
            ), (
                main_gun_3_contact,
                self.bridge_and_main_guns_message_group
            )
        ]
        gun_officer = Agent(
            '炮術長@射擊指揮所',
            [
                # 望遠鏡
                # 測距儀
                # 瞄準
                # 獲取主砲1狀況
                # 獲取主砲2狀況
                # 獲取主砲3狀況
            ], [
                self.bridge_speech.send,
                self.bridge_speech.history,
                self.bridge_and_main_guns_message_group.send,
            ]
        )
        self.people_in_bridge.append(gun_officer)
        self.torpedo_launchers = [
            Torpedo_610mm_Launcher(staff_on_duty=5, staff_off_duty=10,
                                    num_tubes=3, reload_time=1,
                                    full_reload_time=90, torpedoes=6,
                                    tube_rotation=True),
            Torpedo_610mm_Launcher(staff_on_duty=5, staff_off_duty=10,
                                    num_tubes=3, reload_time=1,
                                    full_reload_time=90, torpedoes=6,
                                    tube_rotation=True),
            Torpedo_610mm_Launcher(staff_on_duty=5, staff_off_duty=10,
                                    num_tubes=3, reload_time=1,
                                    full_reload_time=90, torpedoes=6,
                                    tube_rotation=True),
        ]
        self.bridge_and_torpedo_launchers_message_group = Channel('艦橋-魚雷通訊')
        torpedo_launchers_1_contact = Agent(
            '水雷砲台長@一號水雷砲台部',
            [
                self.torpedo_launchers[0].load_torpedoes,
                self.torpedo_launchers[0].prepare_launch,
                self.torpedo_launchers[0].launch_torpedo,
                self.torpedo_launchers[0].post_launch,
                self.torpedo_launchers[0].reload,
                self.torpedo_launchers[0].fault,
                self.torpedo_launchers[0].damage,
                self.torpedo_launchers[0].add_casualties,
                self.torpedo_launchers[0].recall_staff
            ], [
                self.bridge_and_torpedo_launchers_message_group.send,
                self.bridge_and_torpedo_launchers_message_group.history,
            ]
        )
        torpedo_launchers_2_contact = Agent(
            '水雷砲台長@二號水雷砲台部',
            [
                self.torpedo_launchers[1].load_torpedoes,
                self.torpedo_launchers[1].prepare_launch,
                self.torpedo_launchers[1].launch_torpedo,
                self.torpedo_launchers[1].post_launch,
                self.torpedo_launchers[1].reload,
                self.torpedo_launchers[1].fault,
                self.torpedo_launchers[1].damage,
                self.torpedo_launchers[1].add_casualties,
                self.torpedo_launchers[1].recall_staff
            ], [
                self.bridge_and_torpedo_launchers_message_group.send,
                self.bridge_and_torpedo_launchers_message_group.history,
            ]
        )
        torpedo_launchers_3_contact = Agent(
            '水雷砲台長@三號水雷砲台部',
            [
                self.torpedo_launchers[2].load_torpedoes,
                self.torpedo_launchers[2].prepare_launch,
                self.torpedo_launchers[2].launch_torpedo,
                self.torpedo_launchers[2].post_launch,
                self.torpedo_launchers[2].reload,
                self.torpedo_launchers[2].fault,
                self.torpedo_launchers[2].damage,
                self.torpedo_launchers[2].add_casualties,
                self.torpedo_launchers[2].recall_staff
            ], [
                self.bridge_and_torpedo_launchers_message_group.send,
                self.bridge_and_torpedo_launchers_message_group.history,
            ]
        )
        self.actors += [
            (
                torpedo_launchers_1_contact,
                self.bridge_and_torpedo_launchers_message_group
            ), (
                torpedo_launchers_2_contact,
                self.bridge_and_torpedo_launchers_message_group
            ), (
                torpedo_launchers_3_contact,
                self.bridge_and_torpedo_launchers_message_group
            )
        ]
        torpedo_officer = Agent(
            '水雷長@艦橋',
            [
                # 測距儀
                # 瞄準
                # 獲取1號水雷砲台部狀況
                # 獲取2號水雷砲台部狀況
                # 獲取3號水雷砲台部狀況
            ], [
                self.bridge_speech.send,
                self.bridge_speech.history,
                self.bridge_and_torpedo_launchers_message_group.send,
                self.bridge_and_torpedo_launchers_message_group.history,
            ]
        )
        self.people_in_bridge.append(torpedo_officer)
        r_officer = Agent(
            '通信長@艦橋',
            [
                RADIO_CHANNEL.send,
                RADIO_CHANNEL.get_new,
                RADIO_CHANNEL.history,
            ], [
                self.bridge_speech.send,
                self.bridge_speech.history,
                self.bridge_and_torpedo_launchers_message_group.send,
                self.bridge_and_torpedo_launchers_message_group.history,
            ]
        )
        self.people_in_bridge.append(r_officer)
        self.direction = 0
        driver = Agent(
            '舵手@艦橋',
            [
                self.set_direction,
            ], [
                self.bridge_speech.send,
                self.bridge_speech.history,
            ]
        )
        self.people_in_bridge.append(driver)

    def move(self, hours=0.0833):
        self.location = distance(
            miles=self.engine_room.speed * hours
        ).destination(
            self.location,
            bearing=self.direction)

    def set_direction(self, direction):
        self.direction = direction % 360
        return self.direction

    def hit_on(self, by):
        # 最終損害=攻擊力−防禦力+隨機因子最終損害 = 攻擊力 - 防禦力 + 隨機因子
        if by == 'gun':
            # 对于命中具体的舰艇部位，游戏可能会使用一个随机分配系统或预定义的概率表。例如：

            # 鐵炮塔：10% - 20% 的概率
            # 魚雷發射器：5% - 15% 的概率
            # 輪機艙：20% - 30% 的概率（因为这是一个较大的目标）
            # 艦橋：5% - 10% 的概率（因为这是一个较小的目标）
            # 彈藥庫
            self.hp -= 0
        elif by == 'torpedo':
            # 輪機艙：20% - 30% 的概率（因为这是一个较大的目标）
            self.hp -= 0

    def next(self):
        for officer in self.people_in_bridge:
            pass
        for actor, channel in self.actors:
            pass