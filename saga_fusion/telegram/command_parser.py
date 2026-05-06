import types
from .telegram_types import RiskLevel

class CommandParser:
    def __init__(self):
        self.commands = [
            'start', 'status', 'mission', 'scope', 'evidence', 'findings', 'report', 'approve', 'deny', 'logs',
            'create', 'run'
        ]

    def parse(self, text: str):
        """Parse a command string like '/status' or '/mission create VPS'."""
        text = text.strip()
        if not text.startswith('/'):
            return None
        parts = text[1:].split()
        if not parts:
            return None
        command = parts[0]
        args = parts[1:]

        cmd = types.SimpleNamespace()
        cmd.command = command
        cmd.args = args
        cmd.raw = text
        cmd.known = command in self.commands
        return cmd

    def classify_risk(self, cmd):
        command = getattr(cmd, 'command', '') if cmd is not None else ''

        if command in ('status', 'start'):
            return RiskLevel.R0
        if command in ('evidence', 'findings', 'logs'):
            return RiskLevel.R1
        if command == 'report':
            return RiskLevel.R2
        if command in ('scope', 'create'):
            return RiskLevel.R3
        if command in ('mission', 'run'):
            return RiskLevel.R4
        return RiskLevel.R0
