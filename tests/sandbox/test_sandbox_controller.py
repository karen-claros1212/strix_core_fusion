import unittest
from unittest.mock import patch, MagicMock
from saga_fusion.runtime.sandbox.sandbox_types import SandboxConfig, SandboxAction, SandboxResult, RiskLevel
from saga_fusion.runtime.sandbox.sandbox_controller import SandboxController

class TestSandboxController(unittest.TestCase):
    def setUp(self):
        self.config = SandboxConfig(
            workspace_root="/workspace",
            mode="dry_run"
        )
        self.controller = SandboxController(self.config)

    def test_validate_action_success(self):
        action = SandboxAction(
            action_type="list",
            command="ls",
            args=["-la"],
            workspace_path="/workspace/file.txt",
            risk_level=RiskLevel.R0
        )
        self.assertTrue(self.controller.validate_action(action))

    def test_validate_action_block_r5(self):
        action = SandboxAction(
            action_type="delete",
            command="rm",
            args=["-rf", "/"],
            risk_level=RiskLevel.R5
        )
        self.assertFalse(self.controller.validate_action(action))

    def test_execute_dry_run(self):
        action = SandboxAction(
            action_type="list",
            command="ls",
            args=["-la"],
            workspace_path="/workspace",
            risk_level=RiskLevel.R0
        )
        result = self.controller.execute(action)
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Dry run successful")

    @patch('saga_fusion.runtime.sandbox.sandbox_controller.subprocess.run')
    def test_execute_real_command_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "file1\nfile2"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        self.config.mode = "local"
        controller = SandboxController(self.config)

        action = SandboxAction(
            action_type="list",
            command="ls",
            args=["-la"],
            workspace_path="/workspace",
            risk_level=RiskLevel.R0
        )
        result = controller.execute(action)
        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "file1\nfile2")

if __name__ == '__main__':
    unittest.main()
