from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDList
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from datetime import datetime
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.image import AsyncImage
import os

class MessageCard(MDCard):
    def __init__(self, message, is_own, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = dp(10)
        self.spacing = dp(10)
        self.elevation = 0
        self.radius = [dp(10)]
        app = MDApp.get_running_app()
        
        # Аватар
        avatar_box = BoxLayout(
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            padding=0
        )
        
        # Проверяем наличие аватара
        pp = MDApp.get_running_app()
        avatar_path = message.get('avatar_path', app.default_avatar)
        
        self.avatar = AsyncImage(
            source=avatar_path,
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            fit_mode="cover"
        )
        avatar_box.add_widget(self.avatar)
        
        # Контент сообщения
        content = BoxLayout(orientation='vertical')
        username = message['username']
        time_str = datetime.strptime(message['timestamp'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M")
        
        header = BoxLayout(size_hint_y=None, height=dp(20))
        from kivymd.uix.label import MDLabel
        header.add_widget(MDLabel(
            text=f"{username} • {time_str}",
            theme_text_color="Secondary",
            font_style="Caption"
        ))
        
        content.add_widget(header)
        content.add_widget(MDLabel(
            text=message['text'],
            theme_text_color="Primary"
        ))
        
        if is_own:
            self.md_bg_color = [0.9, 0.9, 1, 0.2]
            
        self.add_widget(avatar_box)
        self.add_widget(content)

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        
        
    def setup_ui(self):
        app = MDApp.get_running_app()
        # Основной layout
        self.layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Верхняя панель (прикрепленная к верху)
        self.toolbar = MDTopAppBar(
            title="Чат",
            elevation=4,
            pos_hint={"top": 1},
            md_bg_color=app.theme_cls.primary_color,  # Используем theme_cls из app
            specific_text_color=app.theme_cls.primary_light,  # Используем theme_cls из app
            right_action_items=[
                ["theme-light-dark", lambda x: self.toggle_theme()],
                ["account", lambda x: self.goto_profile()],
                ["logout", lambda x: self.show_logout_dialog()],
                ["refresh", lambda x: self.refresh_messages()]
            ]
        )
        
        # Контейнер для содержимого
        content_layout = BoxLayout(orientation='vertical')
        
        # Область сообщений
        self.scroll = ScrollView()
        self.messages_list = MDList(spacing=dp(10), padding=dp(10))
        self.scroll.add_widget(self.messages_list)
        
        # Область ввода
        input_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10),
            spacing=dp(10)
        )
        
        self.message_input = MDTextField(
            hint_text="Введите сообщение...",
            multiline=False,
            on_text_validate=self.send_message
        )
        
        send_button = MDIconButton(
            icon="send",
            on_release=self.send_message
        )
        
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_button)
        
        # Добавляем элементы в контейнер содержимого
        content_layout.add_widget(self.scroll)
        content_layout.add_widget(input_layout)
        
        # Добавляем toolbar и контент в основной layout
        self.layout.add_widget(self.toolbar)
        self.layout.add_widget(content_layout)
        
        self.add_widget(self.layout)

    def send_message(self, *args):
        text = self.message_input.text.strip()
        if not text:
            return

        app = MDApp.get_running_app()
        app.db.save_message(
            user_id=app.current_user['id'],
            username=app.current_user['username'],
            text=text
        )
        
        self.message_input.text = ""
        self.refresh_messages()

    def refresh_messages(self, *args):
        """Обновление списка сообщений"""
        app = MDApp.get_running_app()
        
        # Проверяем, авторизован ли пользователь
        if not hasattr(app, 'current_user'):
            self.manager.current = 'login'
            return
            
        messages = app.db.get_messages()
        
        self.messages_list.clear_widgets()
        
        for message in messages:
            is_own = message['user_id'] == app.current_user['id']
            message_card = MessageCard(message, is_own)
            self.messages_list.add_widget(message_card)
        
        self.scroll.scroll_y = 0

    def show_logout_dialog(self):
        self.dialog = MDDialog(
            title="Выход",
            text="Вы уверены, что хотите выйти?",
            buttons=[
                MDRaisedButton(
                    text="Отмена",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Выйти",
                    on_release=self.logout
                ),
            ],
        )
        self.dialog.open()

    def logout(self, *args):
        app = MDApp.get_running_app()
        if hasattr(app, 'current_user'):
            delattr(app, 'current_user')
        self.dialog.dismiss()
        self.manager.current = 'login'

    def goto_profile(self):
        self.manager.current = 'profile'

    def toggle_theme(self):
        app = MDApp.get_running_app()
        app.toggle_theme()

    def on_enter(self):
        """При входе на экран"""
        app = MDApp.get_running_app()
        if not hasattr(app, 'current_user'):
            self.manager.current = 'login'
            return
            
        # Запускаем обновление сообщений
        self.refresh_messages()
        Clock.schedule_interval(self.refresh_messages, 3)

    def on_leave(self):
        """При уходе с экрана"""
        Clock.unschedule(self.refresh_messages)