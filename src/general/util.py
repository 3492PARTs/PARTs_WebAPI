from datetime import datetime
from pytz import timezone as pytz_timezone


def date_time_to_mdyhm(date: datetime, time_zone: str | None = None) -> str:
    """
    Convert a datetime object to a formatted string in MM/DD/YYYY, HH:MMam/pm format.
    
    Args:
        date: The datetime object to convert
        time_zone: The timezone to convert to. Defaults to 'America/New_York' if not specified
        
    Returns:
        A formatted string representing the date and time
    """
    local = date.astimezone(pytz_timezone('America/New_York' if time_zone is None else time_zone))
    str = local.strftime("%m/%d/%Y, %I:%M%p")
    return str
