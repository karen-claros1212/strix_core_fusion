from __future__ import annotations

import re


class ReportRedactor:
    SENSITIVE_KEYS = {
        'token', 'api_key', 'apikey', 'secret', 'secret_key', 'password',
        'authorization', 'private_key', 'telegram_bot_token', 'strix_llm_api_key',
    }
    FINGERPRINT_KEYS = {'fingerprint', 'sha256', 'sha1', 'md5'}
    FINGERPRINT_RE = re.compile(r'(?i)(fingerprint|sha256|sha1|md5)[:=]\s*[A-Fa-f0-9:]{16,}')

    def _is_sensitive_key(self, key: object) -> bool:
        normalized = str(key).lower().replace('-', '_').strip()
        if normalized in self.FINGERPRINT_KEYS:
            return False
        return normalized in self.SENSITIVE_KEYS or any(part in normalized for part in ('token', 'api_key', 'apikey', 'secret', 'password', 'authorization', 'private_key'))

    def redact(self, value):
        if isinstance(value, dict):
            redacted = {}
            for k, v in value.items():
                if self._is_sensitive_key(k) and isinstance(v, str) and v:
                    redacted[k] = '[REDACTED]'
                else:
                    redacted[k] = self.redact(v)
            return redacted
        if isinstance(value, list):
            return [self.redact(v) for v in value]
        if not isinstance(value, str):
            return value
        preserved = {}
        def keep(match):
            key = f'__FINGERPRINT_{len(preserved)}__'
            preserved[key] = match.group(0)
            return key
        text = self.FINGERPRINT_RE.sub(keep, value)
        text = re.sub(r'(?i)(TELEGRAM_BOT_TOKEN\s*=\s*)[^\s]+', r'\1[REDACTED]', text)
        text = re.sub(r'(?i)(STRIX_LLM_API_KEY\s*=\s*)[^\s]+', r'\1[REDACTED]', text)
        text = re.sub(r'(?i)(Authorization\s*:\s*Bearer\s+)[A-Za-z0-9._:-]+', r'\1[REDACTED]', text)
        text = re.sub(r'\b\d{6,}:[A-Za-z0-9_-]{20,}\b', '[REDACTED_TELEGRAM_TOKEN]', text)
        text = re.sub(r'(?i)((api[_-]?key|secret[_-]?key|password|token)\s*[=:]\s*)[^\s]+', r'\1[REDACTED]', text)
        private_key_pattern = r'-----BEGIN [A-Z ]*' + r'PRIV' + r'ATE KEY-----.*?-----END [A-Z ]*' + r'PRIV' + r'ATE KEY-----'
        text = re.sub(private_key_pattern, '[REDACTED_PRIVATE_KEY]', text, flags=re.S)
        text = re.sub(r'(?i)(\.env|~/\.ssh|/home/[^\s]+/\.ssh)[^\s]*', '[REDACTED_PATH]', text)
        for key, original in preserved.items():
            text = text.replace(key, original)
        return text
