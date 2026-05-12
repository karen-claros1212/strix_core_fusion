from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class CronExpression:
    raw: str
    minutes: frozenset[int]
    hours: frozenset[int]
    days_of_month: frozenset[int]
    months: frozenset[int]
    days_of_week: frozenset[int]

    def matches(self, dt: datetime) -> bool:
        cron_dow = (dt.weekday() + 1) % 7  # Python Monday=0, cron Sunday=0.
        return (
            dt.minute in self.minutes
            and dt.hour in self.hours
            and dt.day in self.days_of_month
            and dt.month in self.months
            and cron_dow in self.days_of_week
        )


class CronValidationError(ValueError):
    pass


class CronValidator:
    """Small allowlisted five-field cron validator for planning only."""

    RANGES = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))

    def parse(self, expression: str) -> CronExpression:
        raw = str(expression or "").strip()
        if not raw or raw.startswith("@"):
            raise CronValidationError("only five-field cron expressions are supported")
        parts = raw.split()
        if len(parts) != 5:
            raise CronValidationError("cron expression must have exactly five fields")
        values = [self._parse_field(part, *bounds) for part, bounds in zip(parts, self.RANGES)]
        dow = {0 if value == 7 else value for value in values[4]}
        return CronExpression(raw, frozenset(values[0]), frozenset(values[1]), frozenset(values[2]), frozenset(values[3]), frozenset(dow))

    def validate(self, expression: str) -> bool:
        self.parse(expression)
        return True

    def next_run_after(self, expression: str, after: datetime | None = None, max_days: int = 366) -> datetime | None:
        cron = self.parse(expression)
        current = (after or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(second=0, microsecond=0) + timedelta(minutes=1)
        deadline = current + timedelta(days=max_days)
        while current <= deadline:
            if cron.matches(current):
                return current
            current += timedelta(minutes=1)
        return None

    @classmethod
    def _parse_field(cls, field: str, minimum: int, maximum: int) -> set[int]:
        if not field:
            raise CronValidationError("empty cron field")
        values: set[int] = set()
        for token in field.split(','):
            token = token.strip()
            if not token:
                raise CronValidationError("empty cron list item")
            values.update(cls._parse_token(token, minimum, maximum))
        if not values:
            raise CronValidationError("cron field produced no values")
        return values

    @classmethod
    def _parse_token(cls, token: str, minimum: int, maximum: int) -> set[int]:
        if '/' in token:
            base, step_s = token.split('/', 1)
            if not step_s.isdigit() or int(step_s) <= 0:
                raise CronValidationError("cron step must be a positive integer")
            step = int(step_s)
        else:
            base, step = token, 1
        if base == '*':
            start, end = minimum, maximum
        elif '-' in base:
            start_s, end_s = base.split('-', 1)
            if not start_s.isdigit() or not end_s.isdigit():
                raise CronValidationError("cron ranges must be numeric")
            start, end = int(start_s), int(end_s)
        else:
            if not base.isdigit():
                raise CronValidationError("cron fields must be numeric, ranges, lists, *, or steps")
            start = end = int(base)
        if start < minimum or end > maximum or start > end:
            raise CronValidationError("cron field value out of range")
        return set(range(start, end + 1, step))


__all__ = ["CronExpression", "CronValidationError", "CronValidator"]
