from .telegram_types import MissionRequest


class MissionParser:
    def parse(self, text: str, requester_id: str = "", chat_id: str = "") -> MissionRequest:
        normalized = (text or "").strip()
        if not normalized:
            raise ValueError("Empty mission")

        if normalized.startswith("/mission"):
            normalized = normalized[len("/mission"):].strip()
            if not normalized:
                raise ValueError("Empty mission")

        parts = normalized.split(maxsplit=1)
        action_type = parts[0]
        target = parts[1] if len(parts) > 1 else ""

        return MissionRequest(
            requester_id=str(requester_id),
            chat_id=str(chat_id),
            raw_text=text,
            action_type=action_type,
            target=target,
            arguments=target,
        )
