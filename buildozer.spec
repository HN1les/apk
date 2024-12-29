[app]
title = Chat App
package.name = chatapp
package.domain = org.chatapp
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json
version = 1.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,plyer,sqlite3

# Иконка и сплеш
presplash.filename = %(source.dir)s/assets/default_avatar.png
icon.filename = %(source.dir)s/assets/default_avatar.png

# Ориентация
orientation = portrait

# Разрешения
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android настройки
android.api = 33
android.minapi = 21
android.ndk = 23b
android.skip_update = False
android.accept_sdk_license = True
android.arch = armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1