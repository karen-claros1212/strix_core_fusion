import os
from .telegram_gateway import TelegramGateway

class ReportSender:
    def __init__(self, gateway: TelegramGateway):
        self.gateway = gateway

    def send_report(self, chat_id: str, report_path: str):
        """Send a report file to the user."""
        if not os.path.exists(report_path):
            self.gateway.send_message(chat_id, "Report not found.")
            return False
        
        with open(report_path, 'rb') as f:
            content = f.read()
        
        filename = os.path.basename(report_path)
        return self.gateway.send_document(chat_id, content, filename)
