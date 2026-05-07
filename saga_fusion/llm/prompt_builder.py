class PromptBuilder:
    def system_prompt(self) -> str:
        return (
            "You are the STRIX Saga Fusion brain. You reason and structure requests only. "
            "Never execute tools, never approve R4, never execute R5, and never bypass MissionPolicy or SandboxController."
        )

    def mission_prompt(self, text: str, context=None) -> list[dict[str, str]]:
        context_text = "" if context is None else str(context)
        return [
            {"role": "system", "content": self.system_prompt()},
            {
                "role": "user",
                "content": (
                    "Convert this natural language request into compact JSON with keys "
                    "action_type, target, arguments, summary. Do not execute anything.\n"
                    f"Context: {context_text}\nRequest: {text}"
                ),
            },
        ]

    def analysis_prompt(self, text: str, context=None) -> list[dict[str, str]]:
        context_text = "" if context is None else str(context)
        return [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": f"Analyze safely without executing. Context: {context_text}\nText: {text}"},
        ]
