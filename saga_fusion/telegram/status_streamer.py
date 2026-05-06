class StatusStreamer:
    def __init__(self, gateway):
        self.gateway = gateway

    def send_status(self, chat_id, status_text):
        self.gateway.send_message(chat_id, status_text)
