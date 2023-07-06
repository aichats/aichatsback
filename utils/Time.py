from datetime import datetime, timedelta


def now(utc_offset=timedelta(hours=5, minutes=30)) -> datetime:  # default ist
    now_utc = datetime.utcnow()
    # utc_offset = datetime.timedelta(hours=5, minutes=30)
    now_ist = now_utc + utc_offset
    # print(f"UTC time: {now_utc}")
    # print(f"IST time: {now_ist}")
    return now_ist


def now_utc():
    return now(timedelta())


def today():
    from datetime import datetime as dt
    x = dt.now()
    x = x.replace(second=0, microsecond=0)
    return x


def deltaTime(min=1, sec=0, hour=0, day=0):
    from datetime import timedelta as td
    return td(minutes=min, seconds=sec, days=day, hours=hour)


def futureTime(date=today(), min=1):
    return date + deltaTime(min)
