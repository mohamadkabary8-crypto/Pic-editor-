
[app]

# (str) Title of your application
title = Photo Master Pro

# (str) Package name
package.name = photomasterpro

# (str) Package domain (needed for android packaging)
package.domain = org.photomaster

# (str) Source files where the application lives (relative to .spec)
source.dir = .

# (list) Source files to include (let empty to include all files)
source.exts = py,png,jpg,kv,atlas

# (list) Application requirements
# رول‌کننده پیش‌فرض کیوی، پایتون و پری‌لودهای ضروری
requirements = python3,kivy,pillow

# (str) Supported orientations
orientation = portrait

# (list) The gles version to use
fullscreen = 0

# (string) Preserver orientation on tablet
# orientation = landscape

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/presplash.png

# (list) Supported architectures
android.archs = arm64-v8a, armeabi-v7a

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
# android.ndk = 25b

# (bool) Use Android X
android.androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_root = 0
