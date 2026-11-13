import datetime as dt
import json
import os
import time

from prayer import day_events, local_now

HERE = os.path.dirname(os.path.abspath(__file__))
ADHAN_FILE = os.path.join(HERE, "adhan.mp3")
CHANNEL = "adhan_alerts"


def notify(title, text, adhan=False):
    try:
        from jnius import autoclass
        String = autoclass("java.lang.String")
        ctx = autoclass("org.kivy.android.PythonService").mService
        Context = autoclass("android.content.Context")
        Channel = autoclass("android.app.NotificationChannel")
        Builder = autoclass("android.app.Notification$Builder")
        BigText = autoclass("android.app.Notification$BigTextStyle")
        icon = autoclass("android.R$drawable").ic_lock_idle_alarm
        nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE)
        nm.createNotificationChannel(Channel(CHANNEL, String("تذكير الصلاة والأذكار"), 4))
        b = Builder(ctx, CHANNEL)
        b.setContentTitle(String(title))
        b.setContentText(String(text))
        b.setStyle(BigText().bigText(String(text)))
        b.setSmallIcon(icon)
        b.setAutoCancel(True)
        nm.notify(int(time.time()) % 100000, b.build())
    except Exception as e:
        print("notify failed:", e)
    if adhan and os.path.exists(ADHAN_FILE):
        try:
            from jnius import autoclass
            mp = autoclass("android.media.MediaPlayer")()
            mp.setDataSource(ADHAN_FILE)
            mp.prepare()
            mp.start()
        except Exception as e:
            print("audio failed:", e)


def main():
    cfg = json.loads(os.environ.get("PYTHON_SERVICE_ARGUMENT", "{}") or "{}")
    lat = cfg.get("lat", 30.0444)
    lng = cfg.get("lng", 31.2357)
    notify("تم إدخال الإسلام إلى هاتفك ✅", "تذكير الصلاة والأذكار شغال بإذن الله. تقدر توقفه من التطبيق في أي وقت.")

    while True:
        now = local_now()
        events = []
        for k in range(2):
            events += day_events(now.date() + dt.timedelta(days=k), lat, lng)
        nxt = None
        for e in sorted(events, key=lambda x: x[0]):
            if e[0] > now:
                nxt = e
                break
        while local_now() < nxt[0]:
            time.sleep(15)
        if (local_now() - nxt[0]).total_seconds() < 600:
            notify(nxt[1], nxt[2], nxt[3])


main()
