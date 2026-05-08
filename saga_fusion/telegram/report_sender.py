import os
from .telegram_gateway import TelegramGateway
from ..reporting import ReportBuilder, TelegramReportFormatter

class ReportSender:
    def __init__(self, gateway: TelegramGateway):
        self.gateway = gateway
        self.builder = ReportBuilder()
        self.formatter = TelegramReportFormatter()

    def send_report(self, chat_id: str, report_path: str):
        """Send a report file to the user."""
        if not os.path.exists(report_path):
            self.gateway.send_message(chat_id, "Report not found.")
            return False

        try:
            report = self.builder.build_from_evidence(report_path, audience="telegram_summary")
            summary = self.formatter.format(report, artifact_ref=report_path)
            self.gateway.send_message(chat_id, summary)
        except Exception:
            self.gateway.send_message(chat_id, f"Report artifact: {report_path}")
        
        with open(report_path, 'rb') as f:
            content = f.read()
        
        filename = os.path.basename(report_path)
        return self.gateway.send_document(chat_id, content, filename)
