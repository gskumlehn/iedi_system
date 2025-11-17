from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

class DateUtils:

    BRAZIL_TZ = "America/Sao_Paulo"
    UTC_TZ = "UTC"

    @staticmethod
    def to_iso_format(dt: datetime, tz: str = BRAZIL_TZ) -> str:
        return dt.astimezone(ZoneInfo(tz)).strftime("%Y-%m-%dT%H:%M:%S%z")

    @staticmethod
    def from_date_and_time(date_str: str, time_str: str, tz: str = BRAZIL_TZ) -> datetime:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        return dt.replace(tzinfo=ZoneInfo(tz))

    @staticmethod
    def subtract_days(base_datetime: datetime, days: int) -> datetime:
        return base_datetime - timedelta(days=days)

    @staticmethod
    def to_utc(dt: datetime, assume_tz: str = BRAZIL_TZ) -> datetime:
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(assume_tz))
        return dt.astimezone(timezone.utc)

    @staticmethod
    def parse_date(date_string: str):
        try:
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            return None
