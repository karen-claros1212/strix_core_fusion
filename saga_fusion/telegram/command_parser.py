import types
from .telegram_types import RiskLevel

class CommandParser:
    def __init__(self):
        # Telegram UX is natural-first. Slash commands are limited to
        # admin/debug controls; operational workflows are invoked by natural
        # language and routed through STRIX Core first.
        self.commands = ['status', 'help', 'approve', 'deny', 'report']

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

        if command in ('status', 'help'):
            return RiskLevel.R0
        if command == 'report':
            return RiskLevel.R2
        if command in ('approve', 'deny'):
            return RiskLevel.R4
        return RiskLevel.R0
