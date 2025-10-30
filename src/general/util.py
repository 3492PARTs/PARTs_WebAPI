import pytz

def date_time_to_mdyhm(date, time_zone=None):
    local = date.astimezone(pytz.timezone('America/New_York' if time_zone is None else time_zone))
    str = local.strftime("%m/%d/%Y, %I:%M%p")
    return str