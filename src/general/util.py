from pytz import timezone as pytz_timezone

def date_time_to_mdyhm(date, time_zone=None):
    local = date.astimezone(pytz_timezone('America/New_York' if time_zone is None else time_zone))
    str = local.strftime("%m/%d/%Y, %I:%M%p")
    return str
