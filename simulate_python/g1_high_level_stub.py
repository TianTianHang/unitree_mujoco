import json
import sys
import time
from dataclasses import dataclass
from threading import Thread

try:
    from unitree_sdk2py.core.channel import ChannelPublisher
    from unitree_sdk2py.g1.arm.g1_arm_action_api import (
        ARM_ACTION_API_VERSION,
        ARM_ACTION_SERVICE_NAME,
        ROBOT_API_ID_ARM_ACTION_EXECUTE_ACTION,
        ROBOT_API_ID_ARM_ACTION_GET_ACTION_LIST,
    )
    from unitree_sdk2py.g1.audio.g1_audio_api import (
        AUDIO_API_VERSION,
        AUDIO_SERVICE_NAME,
        ROBOT_API_ID_AUDIO_ASR,
        ROBOT_API_ID_AUDIO_GET_VOLUME,
        ROBOT_API_ID_AUDIO_SET_RGB_LED,
        ROBOT_API_ID_AUDIO_SET_VOLUME,
        ROBOT_API_ID_AUDIO_START_PLAY,
        ROBOT_API_ID_AUDIO_STOP_PLAY,
        ROBOT_API_ID_AUDIO_TTS,
    )
    try:
        from unitree_sdk2py.idl.unitree_hg.msg.dds_ import SportModeState_
    except (ImportError, ModuleNotFoundError):
        try:
            import cyclonedds.idl as idl
            import cyclonedds.idl.annotations as annotate
            import cyclonedds.idl.types as types

            @dataclass
            @annotate.final
            @annotate.autoid("sequential")
            class SportModeState_(
                idl.IdlStruct, typename="unitree_hg.msg.dds_.SportModeState_"
            ):
                fsm_id: types.uint32 = 0
                fsm_mode: types.uint32 = 0
                task_id: types.uint32 = 0
                task_time: types.float32 = 0.0

        except (ImportError, ModuleNotFoundError):

            @dataclass
            class SportModeState_:
                fsm_id: int = 0
                fsm_mode: int = 0
                task_id: int = 0
                task_time: float = 0.0

    from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_
    from unitree_sdk2py.g1.loco.g1_loco_api import (
        LOCO_API_VERSION,
        LOCO_SERVICE_NAME,
        ROBOT_API_ID_LOCO_GET_BALANCE_MODE,
        ROBOT_API_ID_LOCO_GET_FSM_ID,
        ROBOT_API_ID_LOCO_GET_FSM_MODE,
        ROBOT_API_ID_LOCO_GET_PHASE,
        ROBOT_API_ID_LOCO_GET_STAND_HEIGHT,
        ROBOT_API_ID_LOCO_GET_SWING_HEIGHT,
        ROBOT_API_ID_LOCO_SET_ARM_TASK,
        ROBOT_API_ID_LOCO_SET_BALANCE_MODE,
        ROBOT_API_ID_LOCO_SET_FSM_ID,
        ROBOT_API_ID_LOCO_SET_STAND_HEIGHT,
        ROBOT_API_ID_LOCO_SET_SWING_HEIGHT,
        ROBOT_API_ID_LOCO_SET_VELOCITY,
    )
    from unitree_sdk2py.rpc.server import Server
except ModuleNotFoundError:
    ARM_ACTION_SERVICE_NAME = "arm"
    ARM_ACTION_API_VERSION = "1.0.0.14"
    ROBOT_API_ID_ARM_ACTION_EXECUTE_ACTION = 7106
    ROBOT_API_ID_ARM_ACTION_GET_ACTION_LIST = 7107

    AUDIO_SERVICE_NAME = "voice"
    AUDIO_API_VERSION = "1.0.0.0"
    ROBOT_API_ID_AUDIO_TTS = 1001
    ROBOT_API_ID_AUDIO_ASR = 1002
    ROBOT_API_ID_AUDIO_START_PLAY = 1003
    ROBOT_API_ID_AUDIO_STOP_PLAY = 1004
    ROBOT_API_ID_AUDIO_GET_VOLUME = 1005
    ROBOT_API_ID_AUDIO_SET_VOLUME = 1006
    ROBOT_API_ID_AUDIO_SET_RGB_LED = 1010

    LOCO_SERVICE_NAME = "sport"
    LOCO_API_VERSION = "1.0.0.0"
    ROBOT_API_ID_LOCO_GET_FSM_ID = 7001
    ROBOT_API_ID_LOCO_GET_FSM_MODE = 7002
    ROBOT_API_ID_LOCO_GET_BALANCE_MODE = 7003
    ROBOT_API_ID_LOCO_GET_SWING_HEIGHT = 7004
    ROBOT_API_ID_LOCO_GET_STAND_HEIGHT = 7005
    ROBOT_API_ID_LOCO_GET_PHASE = 7006
    ROBOT_API_ID_LOCO_SET_FSM_ID = 7101
    ROBOT_API_ID_LOCO_SET_BALANCE_MODE = 7102
    ROBOT_API_ID_LOCO_SET_SWING_HEIGHT = 7103
    ROBOT_API_ID_LOCO_SET_STAND_HEIGHT = 7104
    ROBOT_API_ID_LOCO_SET_VELOCITY = 7105
    ROBOT_API_ID_LOCO_SET_ARM_TASK = 7106

    class String_:
        def __init__(self, data: str = ""):
            self.data = data

    @dataclass
    class SportModeState_:
        fsm_id: int = 0
        fsm_mode: int = 0
        task_id: int = 0
        task_time: float = 0.0

    class ChannelPublisher:
        def __init__(self, _name: str, _type):
            pass

        def Init(self):
            pass

        def Write(self, _sample, _timeout=None):
            return True

    class Server:
        def __init__(self, _name: str):
            pass

        def _SetApiVersion(self, _api_version: str):
            pass

        def _RegistHandler(self, _api_id: int, _handler, _check_lease: int):
            pass

        def Start(self, _enable_prio_queue: bool = False):
            raise RuntimeError("unitree_sdk2py is required to start DDS RPC stubs")


def _json_data(value):
    return json.dumps({"data": value})


def _parse_json(parameter: str):
    if not parameter:
        return {}
    return json.loads(parameter)


ASR_TOPIC = "rt/audio_msg"
SPORT_MODE_STATE_TOPIC = "rt/sportmodestate"


def g1_asr_payload(line: str, *, index: int = 1, timestamp: int | None = None) -> str:
    text = line.strip()
    if not text:
        raise ValueError("ASR input line cannot be empty")

    timestamp = int(time.time() * 1000) if timestamp is None else timestamp
    defaults = {
        "index": index,
        "timestamp": timestamp,
        "text": text,
        "angle": 0,
        "speaker_id": 0,
        "sense": "neutral",
        "confidence": 1.0,
        "language": "zh",
        "is_final": 1,
    }

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = defaults
    else:
        if not isinstance(payload, dict):
            raise ValueError("ASR JSON input must be an object")
        payload = {**defaults, **payload}

    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


class G1AsrStdinPublisher:
    def __init__(self, topic: str = ASR_TOPIC, stdin=None, publisher=None):
        self.topic = topic
        self.stdin = stdin or sys.stdin
        self.publisher = publisher or ChannelPublisher(topic, String_)
        self.index = 0

    def Init(self):
        self.publisher.Init()

    def publish_line(self, line: str):
        if not line.strip():
            return False

        self.index += 1
        payload = g1_asr_payload(line, index=self.index)
        return self.publisher.Write(String_(payload))

    def Run(self):
        print(
            "[G1HighLevelStub] ASR stdin publisher started; "
            "type text or ASR JSON lines to publish rt/audio_msg"
        )
        for line in self.stdin:
            try:
                if self.publish_line(line):
                    print(f"[G1HighLevelStub] asr -> {line.strip()}")
                else:
                    print("[G1HighLevelStub] asr skipped empty line")
            except Exception as error:
                print(f"[G1HighLevelStub] asr publish error: {error}")

    def Start(self):
        thread = Thread(target=self.Run, name="g1_asr_stdin", daemon=True)
        thread.start()
        return thread


@dataclass
class G1LocoStubState:
    fsm_id: int = 500
    fsm_mode: int = 0
    balance_mode: int = 0
    swing_height: float = 0.0
    stand_height: float = 0.0
    phase: str = "stub"
    velocity: tuple = (0.0, 0.0, 0.0)
    velocity_duration: float = 0.0
    velocity_duration_is_continuous: bool = False
    arm_task_id: int = 0
    arm_task_start_time: float | None = None

    def task_time(self) -> float:
        if self.arm_task_id == 0 or self.arm_task_start_time is None:
            return 0.0
        return max(0.0, time.monotonic() - self.arm_task_start_time)


class G1SportModeStatePublisher:
    def __init__(
        self,
        state=None,
        topic: str = SPORT_MODE_STATE_TOPIC,
        publisher=None,
        interval: float = 0.05,
    ):
        self.state = state or G1LocoStubState()
        self.topic = topic
        self.publisher = publisher or ChannelPublisher(topic, SportModeState_)
        self.interval = interval

    def Init(self):
        self.publisher.Init()

    def sample(self):
        return SportModeState_(
            fsm_id=int(self.state.fsm_id),
            fsm_mode=int(self.state.fsm_mode),
            task_id=int(self.state.arm_task_id),
            task_time=float(self.state.task_time()),
        )

    def publish_once(self):
        return self.publisher.Write(self.sample())

    def Run(self):
        print(
            "[G1HighLevelStub] SportModeState publisher started; "
            f"publishing {self.topic}"
        )
        while True:
            try:
                self.publish_once()
            except Exception as error:
                print(f"[G1HighLevelStub] sport-state publish error: {error}")
            time.sleep(self.interval)

    def Start(self):
        thread = Thread(target=self.Run, name="g1_sport_state", daemon=True)
        thread.start()
        return thread


class G1LocoStubServer(Server):
    def __init__(self, state=None):
        super().__init__(LOCO_SERVICE_NAME)
        self.state = state or G1LocoStubState()

    def Init(self):
        self._SetApiVersion(LOCO_API_VERSION)
        self._RegistHandler(ROBOT_API_ID_LOCO_GET_FSM_ID, self.GetFsmId, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_GET_FSM_MODE, self.GetFsmMode, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_GET_BALANCE_MODE, self.GetBalanceMode, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_GET_SWING_HEIGHT, self.GetSwingHeight, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_GET_STAND_HEIGHT, self.GetStandHeight, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_GET_PHASE, self.GetPhase, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_SET_FSM_ID, self.SetFsmId, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_SET_BALANCE_MODE, self.SetBalanceMode, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_SET_SWING_HEIGHT, self.SetSwingHeight, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_SET_STAND_HEIGHT, self.SetStandHeight, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_SET_VELOCITY, self.SetVelocity, 0)
        self._RegistHandler(ROBOT_API_ID_LOCO_SET_ARM_TASK, self.SetArmTask, 0)

    def GetFsmId(self, _parameter: str):
        return 0, _json_data(self.state.fsm_id)

    def GetFsmMode(self, _parameter: str):
        return 0, _json_data(self.state.fsm_mode)

    def GetBalanceMode(self, _parameter: str):
        return 0, _json_data(self.state.balance_mode)

    def GetSwingHeight(self, _parameter: str):
        return 0, _json_data(self.state.swing_height)

    def GetStandHeight(self, _parameter: str):
        return 0, _json_data(self.state.stand_height)

    def GetPhase(self, _parameter: str):
        return 0, _json_data(self.state.phase)

    def SetFsmId(self, parameter: str):
        self.state.fsm_id = int(_parse_json(parameter).get("data", self.state.fsm_id))
        print(f"[G1HighLevelStub] sport SetFsmId -> {self.state.fsm_id}")
        return 0, ""

    def SetBalanceMode(self, parameter: str):
        self.state.balance_mode = int(
            _parse_json(parameter).get("data", self.state.balance_mode)
        )
        print(f"[G1HighLevelStub] sport SetBalanceMode -> {self.state.balance_mode}")
        return 0, ""

    def SetSwingHeight(self, parameter: str):
        self.state.swing_height = float(
            _parse_json(parameter).get("data", self.state.swing_height)
        )
        print(f"[G1HighLevelStub] sport SetSwingHeight -> {self.state.swing_height}")
        return 0, ""

    def SetStandHeight(self, parameter: str):
        self.state.stand_height = float(
            _parse_json(parameter).get("data", self.state.stand_height)
        )
        print(f"[G1HighLevelStub] sport SetStandHeight -> {self.state.stand_height}")
        return 0, ""

    def SetVelocity(self, parameter: str):
        data = _parse_json(parameter)
        velocity = data.get("velocity", self.state.velocity)
        self.state.velocity = tuple(float(value) for value in velocity)
        self.state.velocity_duration = float(data.get("duration", 0.0))
        self.state.velocity_duration_is_continuous = (
            self.state.velocity_duration >= 864000.0
        )
        duration_note = (
            " (SDK continuous-move sentinel)"
            if self.state.velocity_duration_is_continuous
            else ""
        )
        print(
            "[G1HighLevelStub] sport SetVelocity -> "
            f"{self.state.velocity}, duration={self.state.velocity_duration}{duration_note}"
        )
        return 0, ""

    def SetArmTask(self, parameter: str):
        self.state.arm_task_id = int(_parse_json(parameter).get("data", 0))
        print(f"[G1HighLevelStub] sport SetArmTask -> {self.state.arm_task_id}")
        return 0, ""


ACTION_LIST = {
    "release arm": 99,
    "two-hand kiss": 11,
    "left kiss": 12,
    "right kiss": 13,
    "hands up": 15,
    "clap": 17,
    "high five": 18,
    "hug": 19,
    "heart": 20,
    "right heart": 21,
    "reject": 22,
    "right hand up": 23,
    "x-ray": 24,
    "face wave": 25,
    "high wave": 26,
    "shake hand": 27,
}


class G1ArmActionStubServer(Server):
    def __init__(self, state=None):
        super().__init__(ARM_ACTION_SERVICE_NAME)
        self.state = state or G1LocoStubState()
        self.last_action_id = None

    def Init(self):
        self._SetApiVersion(ARM_ACTION_API_VERSION)
        self._RegistHandler(ROBOT_API_ID_ARM_ACTION_EXECUTE_ACTION, self.ExecuteAction, 0)
        self._RegistHandler(ROBOT_API_ID_ARM_ACTION_GET_ACTION_LIST, self.GetActionList, 0)

    def ExecuteAction(self, parameter: str):
        self.last_action_id = int(_parse_json(parameter).get("data", 0))
        self.state.arm_task_id = self.last_action_id
        self.state.arm_task_start_time = time.monotonic()
        print(f"[G1HighLevelStub] arm ExecuteAction -> {self.last_action_id}")
        return 0, ""

    def GetActionList(self, _parameter: str):
        return 0, json.dumps(ACTION_LIST)


class G1AudioStubServer(Server):
    def __init__(self):
        super().__init__(AUDIO_SERVICE_NAME)
        self.volume = 80
        self.last_tts = None
        self.last_led = (0, 0, 0)

    def Init(self):
        self._SetApiVersion(AUDIO_API_VERSION)
        self._RegistHandler(ROBOT_API_ID_AUDIO_TTS, self.TtsMaker, 0)
        self._RegistHandler(ROBOT_API_ID_AUDIO_ASR, self.Asr, 0)
        self._RegistHandler(ROBOT_API_ID_AUDIO_START_PLAY, self.StartPlay, 0)
        self._RegistHandler(ROBOT_API_ID_AUDIO_STOP_PLAY, self.StopPlay, 0)
        self._RegistHandler(ROBOT_API_ID_AUDIO_GET_VOLUME, self.GetVolume, 0)
        self._RegistHandler(ROBOT_API_ID_AUDIO_SET_VOLUME, self.SetVolume, 0)
        self._RegistHandler(ROBOT_API_ID_AUDIO_SET_RGB_LED, self.SetRgbLed, 0)

    def TtsMaker(self, parameter: str):
        data = _parse_json(parameter)
        self.last_tts = {
            "text": data.get("text", ""),
            "speaker_id": int(data.get("speaker_id", 0)),
        }
        print(
            "[G1HighLevelStub] voice TtsMaker -> "
            f"speaker={self.last_tts['speaker_id']}, text={self.last_tts['text']}"
        )
        return 0, ""

    def Asr(self, _parameter: str):
        return 0, ""

    def StartPlay(self, _parameter: str):
        return 0, ""

    def StopPlay(self, _parameter: str):
        return 0, ""

    def GetVolume(self, _parameter: str):
        return 0, json.dumps({"volume": self.volume})

    def SetVolume(self, parameter: str):
        self.volume = int(_parse_json(parameter).get("volume", self.volume))
        print(f"[G1HighLevelStub] voice SetVolume -> {self.volume}")
        return 0, ""

    def SetRgbLed(self, parameter: str):
        data = _parse_json(parameter)
        self.last_led = (
            int(data.get("R", 0)),
            int(data.get("G", 0)),
            int(data.get("B", 0)),
        )
        print(f"[G1HighLevelStub] voice LedControl -> {self.last_led}")
        return 0, ""


def start_g1_high_level_stubs():
    state = G1LocoStubState()
    servers = [
        G1LocoStubServer(state),
        G1ArmActionStubServer(state),
        G1AudioStubServer(),
    ]
    for server in servers:
        server.Init()
        server.Start(False)
    sport_state_publisher = G1SportModeStatePublisher(state)
    sport_state_publisher.Init()
    sport_state_publisher.Start()
    print("[G1HighLevelStub] sport/arm/voice RPC stubs and SportModeState publisher started")
    return [*servers, sport_state_publisher]


def start_g1_asr_stdin_publisher():
    publisher = G1AsrStdinPublisher()
    publisher.Init()
    publisher.Start()
    return publisher
