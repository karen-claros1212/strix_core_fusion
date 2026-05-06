import unittest
from unittest.mock import patch, MagicMock
from saga_fusion.runtime.sandbox.sandbox_types import SandboxConfig
from saga_fusion.runtime.sandbox.resource_limiter import ResourceLimiter

class TestResourceLimiter(unittest.TestCase):
    def setUp(self):
        self.config = SandboxConfig(cpu_limit=1.0, ram_limit_mb=512, timeout_seconds=300)
        self.limiter = ResourceLimiter(self.config)

    def test_get_timeout(self):
        self.assertEqual(self.limiter.get_timeout(), 300)

    @patch('psutil.Process')
    def test_validate_resources_success(self, mock_process):
        mock_instance = MagicMock()
        mock_instance.memory_info.return_value.rss = 1024 * 1024 * 100 # 100MB
        mock_instance.cpu_percent.return_value = 50.0
        mock_process.return_value = mock_instance
        self.assertTrue(self.limiter.validate_resources(1234))

    @patch('psutil.Process')
    def test_validate_resources_memory_exceeded(self, mock_process):
        mock_instance = MagicMock()
        mock_instance.memory_info.return_value.rss = 1024 * 1024 * 600 # 600MB
        mock_instance.cpu_percent.return_value = 50.0
        mock_process.return_value = mock_instance
        self.assertFalse(self.limiter.validate_resources(1234))

if __name__ == '__main__':
    unittest.main()
