from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.chat_screen import ChatScreen
from screens.profile_screen import ProfileScreen
from database import Database
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp
from kivy.core.window import Window
from utils import create_default_avatar

class ChatApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.settings_store = JsonStore('settings.json')
        self.default_avatar = create_default_avatar()
        self.current_user = None
        
        Window.minimum_width = dp(300)
        Window.minimum_height = dp(500)

    def build(self):
        try:
            theme_style = self.settings_store.get('theme')['style']
        except:
            theme_style = 'Light'
            self.settings_store.put('theme', style=theme_style)
            
        self.theme_cls.theme_style = theme_style
        self.theme_cls.primary_palette = "Blue"
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(ProfileScreen(name='profile'))
        return sm

    def toggle_theme(self):
        """Переключение темы и сохранение настройки"""
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
        self.settings_store.put('theme', style=self.theme_cls.theme_style)

if __name__ == '__main__':
    ChatApp().run()