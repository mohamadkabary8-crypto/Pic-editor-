[app]
title = Photo Master Pro
package.name = photomasterpro
package.domain = org.photomaster
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 2.0
requirements = python3,kivy,pillow
orientation = portrait
fullscreen = 0
icon.filename = icon.png

[buildozer]
log_level = 2
warn_on_root = 1
android.api = 31
android.minapi = 21
android.sdk = 30
android.ndk = 25b
android.accept_sdk_license = True
