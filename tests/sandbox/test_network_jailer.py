import unittest
from saga_fusion.runtime.sandbox.sandbox_types import SandboxConfig
from saga_fusion.runtime.sandbox.network_jailer import NetworkJailer

class TestNetworkJailer(unittest.TestCase):
    def setUp(self):
        self.config = SandboxConfig(
            workspace_root="/workspace",
            allowed_networks=["10.0.0.0/8"],
            blocked_networks=["192.168.1.0/24"]
        )
        self.jailer = NetworkJailer(self.config)

    def test_validate_network_allowed_ip(self):
        self.assertTrue(self.jailer.validate_network("10.1.1.1"))

    def test_validate_network_blocked_ip(self):
        self.assertFalse(self.jailer.validate_network("192.168.1.1"))

    def test_validate_network_metadata_ip(self):
        self.assertFalse(self.jailer.validate_network("169.254.169.254"))

    def test_validate_network_empty(self):
        self.assertTrue(self.jailer.validate_network(""))

if __name__ == '__main__':
    unittest.main()
