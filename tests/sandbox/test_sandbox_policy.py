import unittest
from saga_fusion.runtime.sandbox.sandbox_types import SandboxConfig, SandboxAction, RiskLevel
from saga_fusion.runtime.sandbox.sandbox_policy import SandboxPolicy

class TestSandboxPolicy(unittest.TestCase):
    def setUp(self):
        self.config = SandboxConfig(workspace_root="/workspace")
        self.policy = SandboxPolicy(self.config)

    def test_validate_path_in_workspace(self):
        self.assertTrue(self.policy.validate_path("/workspace/file.txt"))

    def test_validate_path_outside_workspace(self):
        self.assertFalse(self.policy.validate_path("/etc/passwd"))

    def test_validate_path_traversal(self):
        self.assertFalse(self.policy.validate_path("/workspace/../etc/passwd"))

    def test_validate_command_r5(self):
        action = SandboxAction(action_type="delete", command="rm", args=["-rf", "/"], risk_level=RiskLevel.R5)
        self.assertFalse(self.policy.validate_command(action))

    def test_validate_command_privileged(self):
        action = SandboxAction(action_type="deploy", command="docker", args=["run", "--privileged"], risk_level=RiskLevel.R3)
        self.assertFalse(self.policy.validate_command(action))

if __name__ == '__main__':
    unittest.main()
