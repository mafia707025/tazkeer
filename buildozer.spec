[app]
title = Tazkeer El Salah
package.name = tazkeer
package.domain = org.abdoz
source.dir = .
source.include_exts = py,png,jpg,kv,mp3
version = 0.1
requirements = python3,kivy==2.3.0,pyjnius,android
orientation = portrait
fullscreen = 0
services = adhan:service.py:foreground:sticky
android.permissions = POST_NOTIFICATIONS,FOREGROUND_SERVICE,VIBRATE,WAKE_LOCK
android.api = 33
android.minapi = 26
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
