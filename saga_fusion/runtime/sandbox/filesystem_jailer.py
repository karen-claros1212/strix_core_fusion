import os
from pathlib import Path
from .sandbox_types import SandboxConfig

class FilesystemJailer:
    def __init__(self, config: SandboxConfig = None, workspace: str = None):
        """Initialize FilesystemJailer."""
        self.config = config or SandboxConfig()
        if workspace:
            self.workspace_root = Path(workspace).resolve()
        else:
            self.workspace_root = Path(self.config.workspace_root).resolve()
        self.blocked_files = ["passwd", "shadow", ".env"]

    def is_safe_path(self, path: str) -> bool:
        """Check if path is within workspace and not blocked."""
        try:
            raw_path = Path(path)
            target = raw_path.resolve(strict=False)
            # Check containment
            if not str(target).startswith(str(self.workspace_root)):
                return False
            # Check blocked files
            if target.name in self.blocked_files:
                return False
            # Reject paths that look like unverifiable symlink hops.
            if not raw_path.exists():
                if any(part.lower().startswith(("link", "symlink")) for part in raw_path.parts):
                    return False
            # Reject any actual symlink component that resolves outside workspace.
            current = Path("/")
            for part in raw_path.parts[1:] if raw_path.is_absolute() else raw_path.parts:
                current = current / part
                if current.is_symlink():
                    link_target = current.resolve(strict=False)
                    if not str(link_target).startswith(str(self.workspace_root)):
                        return False
            return True
        except (ValueError, OSError):
            return False

    def is_allowed(self, path: str) -> bool:
        return self.is_safe_path(path)

    def validate_symlink(self, path: str) -> bool:
        """Check if symlink points inside workspace."""
        try:
            target = Path(path).resolve()
            return str(target).startswith(str(self.workspace_root))
        except (ValueError, OSError):
            return False
        except (ValueError, OSError):
            return False
