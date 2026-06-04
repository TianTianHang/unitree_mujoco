import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "unitree_sdk2_python"))

from g1_high_level_stub import (  # noqa: E402
    ACTION_LIST,
    ASR_TOPIC,
    G1AsrStdinPublisher,
    G1ArmActionStubServer,
    G1AudioStubServer,
    G1LocoStubServer,
    G1LocoStubState,
    G1SportModeStatePublisher,
    SPORT_MODE_STATE_TOPIC,
    SportModeState_,
    String_,
    g1_asr_payload,
)


class FakePublisher:
    def __init__(self):
        self.inited = False
        self.samples = []

    def Init(self):
        self.inited = True

    def Write(self, sample):
        self.samples.append(sample)
        return True


class G1HighLevelStubTest(unittest.TestCase):
    def test_loco_defaults_allow_cli_arm_action_precheck(self):
        server = G1LocoStubServer()

        code, data = server.GetFsmId("{}")

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(data)["data"], 500)

    def test_loco_setters_update_stub_state(self):
        server = G1LocoStubServer()

        self.assertEqual(server.SetFsmId(json.dumps({"data": 1})), (0, ""))
        self.assertEqual(server.SetBalanceMode(json.dumps({"data": 2})), (0, ""))
        self.assertEqual(
            server.SetVelocity(json.dumps({"velocity": [0.1, 0.2, 0.3], "duration": 4.0})),
            (0, ""),
        )

        self.assertEqual(server.state.fsm_id, 1)
        self.assertEqual(server.state.balance_mode, 2)
        self.assertEqual(server.state.velocity, (0.1, 0.2, 0.3))
        self.assertEqual(server.state.velocity_duration, 4.0)
        self.assertFalse(server.state.velocity_duration_is_continuous)

    def test_loco_set_velocity_marks_sdk_continuous_move_sentinel(self):
        server = G1LocoStubServer()

        self.assertEqual(
            server.SetVelocity(
                json.dumps({"velocity": [-0.4, 0.0, 0.0], "duration": 864000.0})
            ),
            (0, ""),
        )

        self.assertEqual(server.state.velocity, (-0.4, 0.0, 0.0))
        self.assertEqual(server.state.velocity_duration, 864000.0)
        self.assertTrue(server.state.velocity_duration_is_continuous)

    def test_sport_mode_state_publisher_uses_shared_loco_state(self):
        state = G1LocoStubState(fsm_id=801, fsm_mode=3, arm_task_id=27)
        state.arm_task_start_time = 100.0
        fake = FakePublisher()
        publisher = G1SportModeStatePublisher(
            state=state, publisher=fake, interval=0.001
        )

        publisher.Init()
        wrote = publisher.publish_once()

        self.assertTrue(fake.inited)
        self.assertTrue(wrote)
        self.assertIsInstance(fake.samples[0], SportModeState_)
        self.assertEqual(fake.samples[0].fsm_id, 801)
        self.assertEqual(fake.samples[0].fsm_mode, 3)
        self.assertEqual(fake.samples[0].task_id, 27)
        self.assertGreaterEqual(fake.samples[0].task_time, 0.0)
        self.assertEqual(publisher.topic, SPORT_MODE_STATE_TOPIC)

    def test_arm_action_updates_shared_sport_mode_task_fields(self):
        state = G1LocoStubState()
        server = G1ArmActionStubServer(state)

        self.assertEqual(server.ExecuteAction(json.dumps({"data": 15})), (0, ""))

        self.assertEqual(state.arm_task_id, 15)
        self.assertIsNotNone(state.arm_task_start_time)

    def test_arm_action_list_matches_known_actions(self):
        server = G1ArmActionStubServer()

        code, data = server.GetActionList("{}")

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(data), ACTION_LIST)

    def test_audio_tts_and_volume_are_recorded(self):
        server = G1AudioStubServer()

        self.assertEqual(
            server.TtsMaker(json.dumps({"text": "hello", "speaker_id": 1})),
            (0, ""),
        )
        self.assertEqual(server.SetVolume(json.dumps({"volume": 42})), (0, ""))
        code, data = server.GetVolume("{}")

        self.assertEqual(server.last_tts, {"text": "hello", "speaker_id": 1})
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(data)["volume"], 42)

    def test_asr_payload_wraps_plain_text_as_final_json(self):
        payload = json.loads(g1_asr_payload("你好", index=7, timestamp=123))

        self.assertEqual(payload["index"], 7)
        self.assertEqual(payload["timestamp"], 123)
        self.assertEqual(payload["text"], "你好")
        self.assertEqual(payload["is_final"], 1)
        self.assertEqual(payload["language"], "zh")

    def test_asr_payload_accepts_json_with_defaults(self):
        payload = json.loads(
            g1_asr_payload('{"text":"站起来","confidence":0.9}', index=2, timestamp=456)
        )

        self.assertEqual(payload["index"], 2)
        self.assertEqual(payload["timestamp"], 456)
        self.assertEqual(payload["text"], "站起来")
        self.assertEqual(payload["confidence"], 0.9)
        self.assertEqual(payload["is_final"], 1)

    def test_asr_stdin_publisher_writes_string_samples(self):
        fake = FakePublisher()
        publisher = G1AsrStdinPublisher(publisher=fake)

        publisher.Init()
        wrote = publisher.publish_line("你好")

        self.assertTrue(fake.inited)
        self.assertTrue(wrote)
        self.assertIsInstance(fake.samples[0], String_)
        self.assertEqual(json.loads(fake.samples[0].data)["text"], "你好")
        self.assertEqual(publisher.topic, ASR_TOPIC)


if __name__ == "__main__":
    unittest.main()
