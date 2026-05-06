import unittest
import tempfile
import os

from saga_fusion.runtime.sandbox.sandbox_policy import SandboxPolicy

class TestSandboxPolicy(unittest.TestCase):
    def setUp(self):
        self.policy = SandboxPolicy()
        self.workspace = tempfile.mkdtemp()
        
    def test_dangerous_command_docker(self):
        result = self.policy.validate_command("docker run alpine")
        self.assertFalse(result['valid'])
        self.assertIn("docker", result['errors'][0])
        
    def test_dangerous_command_kubectl(self):
        result = self.policy.validate_command("kubectl get pods")
        self.assertFalse(result['valid'])
        self.assertIn("kubectl", result['errors'][0])
        
    def test_path_traversal(self):
        result = self.policy.validate_command("cat ../../../etc/passwd")
        self.assertFalse(result['valid'])
        self.assertIn("Path traversal", result['errors'][0])
        
    def test_shadow_file(self):
        result = self.policy.validate_command("cat /etc/shadow")
        self.assertFalse(result['valid'])
        self.assertIn("/etc/shadow", result['errors'][0])
        
    def test_docker_socket(self):
        result = self.policy.validate_command("cat /var/run/docker.sock")
        self.assertFalse(result['valid'])
        self.assertIn("docker.sock", result['errors'][0])
        
    def test_valid_command(self):
        result = self.policy.validate_command("ls -la")
        self.assertTrue(result['valid'])
        
    def test_network_aws_metadata(self):
        result = self.policy.validate_network("169.254.169.254")
        self.assertFalse(result['valid'])
        self.assertIn("Metadata endpoint", result['errors'][0])
        
    def test_network_gcp_metadata(self):
        result = self.policy.validate_network("metadata.google.internal")
        self.assertFalse(result['valid'])
        self.assertIn("Metadata endpoint", result['errors'][0])
        
    def test_network_local_ip(self):
        result = self.policy.validate_network("127.0.0.1")
        self.assertTrue(result['valid'])
        
    def test_network_private_ip(self):
        result = self.policy.validate_network("192.168.1.1")
        self.assertTrue(result['valid'])
        
    def test_filesystem_path_traversal(self):
        result = self.policy.validate_filesystem("../../../etc/passwd", self.workspace)
        self.assertFalse(result['valid'])
        self.assertIn("Path traversal", result['errors'][0])
        
    def test_filesystem_outside_workspace(self):
        result = self.policy.validate_filesystem("/etc/passwd", self.workspace)
        self.assertFalse(result['valid'])
        self.assertIn("Ruta fuera del workspace", result['errors'][0])
        
    def test_filesystem_inside_workspace(self):
        result = self.policy.validate_filesystem("test.txt", self.workspace)
        self.assertTrue(result['valid'])

if __name__ == '__main__':
    unittest.main()