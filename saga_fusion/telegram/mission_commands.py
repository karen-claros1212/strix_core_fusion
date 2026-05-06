class MissionCommands:
    COMMANDS = [
        'start', 'status', 'mission', 'scope', 'evidence', 'findings', 'report', 'approve', 'deny', 'logs'
    ]
    
    def is_valid_command(self, command: str) -> bool:
        return command.lower() in self.COMMANDS
