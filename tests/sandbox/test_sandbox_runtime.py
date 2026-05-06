import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from saga_fusion.runtime.sandbox.sandbox_types import SandboxAction, SandboxMode, ActionType, RiskLevel
from saga_fusion.runtime.sandbox.sandbox_policy import SandboxPolicy
from saga_fusion.runtime.sandbox.filesystem_jailer import FilesystemJailer
from saga_fusion.runtime.sandbox.network_jailer import NetworkJailer
from saga_fusion.runtime.sandbox.resource_limiter import ResourceLimiter
from saga_fusion.runtime.sandbox.sandbox_controller import SandboxController
from saga_fusion.runtime.sandbox.sandbox_audit import SandboxAudit

# --- Test Sandbox Policy ---

def test_policy_allows_r0():
    policy = SandboxPolicy()
    action = SandboxAction(action_type=ActionType.EXECUTE, command="echo hello", mode=SandboxMode.DRY_RUN, risk_level=RiskLevel.R0)
    assert policy.is_allowed(action) == True

def test_policy_blocks_r5():
    policy = SandboxPolicy()
    action = SandboxAction(action_type=ActionType.EXECUTE, command="rm -rf /", mode=SandboxMode.DRY_RUN, risk_level=RiskLevel.R5)
    assert policy.is_allowed(action) == False

def test_policy_blocks_privileged_docker():
    policy = SandboxPolicy()
    action = SandboxAction(action_type=ActionType.EXECUTE, command="docker run --privileged", mode=SandboxMode.DRY_RUN, risk_level=RiskLevel.R4)
    assert policy.is_allowed(action) == False

def test_policy_blocks_docker_sock():
    policy = SandboxPolicy()
    action = SandboxAction(action_type=ActionType.EXECUTE, command="docker run -v /var/run/docker.sock:/var/run/docker.sock", mode=SandboxMode.DRY_RUN, risk_level=RiskLevel.R4)
    assert policy.is_allowed(action) == False

# --- Test Filesystem Jailer ---

def test_filesystem_jailer_allows_workspace():
    jailer = FilesystemJailer(workspace="/workspace")
    assert jailer.is_allowed("/workspace/file.txt") == True

def test_filesystem_jailer_blocks_path_traversal():
    jailer = FilesystemJailer(workspace="/workspace")
    assert jailer.is_allowed("/workspace/../../../etc/passwd") == False

def test_filesystem_jailer_blocks_symlinks():
    jailer = FilesystemJailer(workspace="/workspace")
    # Simulate a symlink to /etc
    assert jailer.is_allowed("/workspace/link_to_etc") == False

# --- Test Network Jailer ---

def test_network_jailer_allows_internal():
    jailer = NetworkJailer()
    assert jailer.is_allowed("127.0.0.1") == True

def test_network_jailer_blocks_metadata():
    jailer = NetworkJailer()
    assert jailer.is_allowed("169.254.169.254") == False

def test_network_jailer_blocks_external():
    jailer = NetworkJailer()
    assert jailer.is_allowed("8.8.8.8") == False

# --- Test Resource Limiter ---

def test_resource_limiter_allows_within_limits():
    limiter = ResourceLimiter(cpu_limit=1.0, memory_limit=1024)
    assert limiter.is_allowed(cpu_usage=0.5, memory_usage=512) == True

def test_resource_limiter_blocks_over_limits():
    limiter = ResourceLimiter(cpu_limit=1.0, memory_limit=1024)
    assert limiter.is_allowed(cpu_usage=1.5, memory_usage=512) == False

# --- Test Sandbox Audit ---

def test_sandbox_audit_logs_action():
    audit = SandboxAudit()
    action = SandboxAction(action_type=ActionType.EXECUTE, command="echo hello", mode=SandboxMode.DRY_RUN, risk_level=RiskLevel.R0)
    audit.log_action(action, {"success": True})
    assert len(audit.logs) > 0

# --- Test Sandbox Controller ---

def test_sandbox_controller_executes_dry_run():
    controller = SandboxController()
    action = SandboxAction(action_type=ActionType.EXECUTE, command="echo hello", mode=SandboxMode.DRY_RUN, risk_level=RiskLevel.R0)
    result = controller.execute(action)
    assert result.success == True

def test_sandbox_controller_blocks_r5():
    controller = SandboxController()
    action = SandboxAction(action_type=ActionType.EXECUTE, command="rm -rf /", mode=SandboxMode.DRY_RUN, risk_level=RiskLevel.R5)
    result = controller.execute(action)
    assert result.success == False
