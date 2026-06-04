import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "unitree_sdk2_python"))


class FakeModel:
    nu = 35
    nsensor = 0
    opt = types.SimpleNamespace(timestep=0.005)


class FakeData:
    sensordata = []


class UnitreeSdk2BridgeTest(unittest.TestCase):
    def test_g1_skips_go_sport_mode_state_publisher(self):
        config = types.SimpleNamespace(ROBOT="g1")
        mujoco = types.SimpleNamespace(
            mj_id2name=lambda *_args: None,
            _enums=types.SimpleNamespace(mjtObj=types.SimpleNamespace(mjOBJ_SENSOR=0)),
        )

        with mock.patch.dict(sys.modules, {"config": config, "mujoco": mujoco}):
            bridge_module = importlib.import_module("unitree_sdk2py_bridge")
            bridge_module = importlib.reload(bridge_module)

        with mock.patch.object(bridge_module, "ChannelPublisher") as publisher:
            with mock.patch.object(bridge_module, "ChannelSubscriber") as subscriber:
                with mock.patch.object(bridge_module, "RecurrentThread") as thread:
                    bridge = bridge_module.UnitreeSdk2Bridge(FakeModel(), FakeData())

        self.assertIsNone(bridge.high_state)
        self.assertIsNone(bridge.high_state_puber)
        self.assertIsNone(bridge.HighStateThread)
        self.assertNotIn(
            bridge_module.TOPIC_HIGHSTATE,
            [call.args[0] for call in publisher.call_args_list],
        )
        subscriber.assert_called_once_with(bridge_module.TOPIC_LOWCMD, bridge_module.LowCmd_)
        self.assertNotIn(
            "sim_highstate",
            [call.kwargs.get("name") for call in thread.call_args_list],
        )


if __name__ == "__main__":
    unittest.main()
