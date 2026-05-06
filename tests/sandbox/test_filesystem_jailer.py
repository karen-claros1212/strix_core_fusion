import unittest
import os
from pathlib import Path
from saga_fusion.runtime.sandbox.sandbox_types import SandboxConfig
from saga_fusion.runtime.sandbox.filesystem_jailer import FilesystemJailer

class TestFilesystemJailer(unittest.TestCase):
    def setUp(self):
        self.config = SandboxConfig(workspace_root="/workspace")
        self.jailer = FilesystemJailer(self.config)

    def test_is_safe_path_in_workspace(self):
        self.assertTrue(self.jailer.is_safe_path("/workspace/file.txt"))

    def test_is_safe_path_outside_workspace(self):
        self.assertFalse(self.jailer.is_safe_path("/etc/passwd"))

    def test_is_safe_path_blocked_file(self):
        self.assertFalse(self.jailer.is_safe_path("/workspace/.env"))

    def test_is_safe_path_traversal(self):
        self.assertFalse(self.jailer.is_safe_path("/workspace/../etc/passwd"))

if __name__ == '__main__':
    unittest.main()
