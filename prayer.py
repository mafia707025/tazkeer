import datetime as dt
import math


def _sin(d):
    return math.sin(math.radians(d))


def _cos(d):
    return math.cos(math.radians(d))


def tz_hours(day):
    try:
        from jnius import autoclass
        TZ = autoclass("java.util.TimeZone")
        noon = dt.datetime(day.year, day.month, day.day, 12, tzinfo=dt.timezone.utc)
        return TZ.getDefault().getOffset(int(noon.timestamp() * 1000)) / 3600000.0
    except Exception:
        return dt.datetime(day.year, day.month, day.day, 12).astimezone().utcoffset().total_seconds() / 3600


def local_now():
    utc = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    return utc + dt.timedelta(hours=tz_hours(utc.date()))


def julian(y, m, d):
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def sun(jd):
    D = jd - 2451545.0
    g = (357.529 + 0.98560028 * D) % 360
    q = (280.459 + 0.98564736 * D) % 360
    L = (q + 1.915 * _sin(g) + 0.020 * _sin(2 * g)) % 360
    e = 23.439 - 0.00000036 * D
    ra = math.degrees(math.atan2(_cos(e) * _sin(L), _cos(L))) / 15 % 24
    decl = math.degrees(math.asin(_sin(e) * _sin(L)))
    eqt = ((q / 15 - ra + 12) % 24) - 12
    return decl, eqt


def prayer_times(day, lat, lng):
    tz = tz_hours(day)
    jd = julian(day.year, day.month, day.day) - lng / 360
    decl, eqt = sun(jd + 0.5)
    dhuhr = 12 + tz - lng / 15 - eqt

    def T(angle):
        x = (-_sin(angle) - _sin(lat) * _sin(decl)) / (_cos(lat) * _cos(decl))
        return math.degrees(math.acos(max(-1, min(1, x)))) / 15

    asr_angle = -math.degrees(math.atan(1 / (1 + math.tan(math.radians(abs(lat - decl))))))
    hours = {
        "fajr": dhuhr - T(19.5),
        "sunrise": dhuhr - T(0.833),
        "dhuhr": dhuhr,
        "asr": dhuhr + T(asr_angle),
        "maghrib": dhuhr + T(0.833),
        "isha": dhuhr + T(17.5),
    }
    base = dt.datetime.combine(day, dt.time())
    return {k: base + dt.timedelta(minutes=round(v * 60)) for k, v in hours.items()}


def day_events(day, lat, lng):
    t = prayer_times(day, lat, lng)
    m = dt.timedelta(minutes=1)
    ev = [
        (t["fajr"], "أذان الفجر", "سنة الفجر ركعتان قبل الفريضة، وهما خير من الدنيا وما فيها.", True),
        (t["fajr"] + 25 * m, "أذكار الصباح", "أصبحنا وأصبح الملك لله... آية الكرسي والمعوذات ٣ مرات.", False),
        (t["sunrise"] + 20 * m, "وقت صلاة الضحى", "ركعتان فأكثر. سنة حلوة تبدأ بيها يومك.", False),
        (t["dhuhr"], "أذان الظهر", "لا تنس السنة الراتبة قبل الظهر وبعده.", True),
        (t["asr"], "أذان العصر", "حافظ على صلاة العصر في وقتها.", True),
        (t["asr"] + 30 * m, "أذكار المساء", "أمسينا وأمسى الملك لله... آية الكرسي والمعوذات ٣ مرات.", False),
        (t["maghrib"], "أذان المغرب", "سنة المغرب ركعتان بعد الفريضة.", True),
        (t["isha"], "أذان العشاء", "سنة العشاء ركعتان بعدها، ولا تنس الوتر قبل النوم.", True),
    ]
    if day.weekday() == 4:
        ev.append((t["dhuhr"] - 60 * m, "يوم الجمعة", "سورة الكهف، والإكثار من الصلاة على النبي ﷺ.", False))
    return ev
