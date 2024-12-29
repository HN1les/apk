from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.core.window import Window

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        Window.bind(on_resize=self.on_window_resize)
        
    def login(self, instance):
        """Обработка входа пользователя"""
        if not self.validate_input():
            return
            
        app = MDApp.get_running_app()
        user = app.db.login_user(self.email.text, self.password.text)
        
        if user:
            app.current_user = user
            self.manager.current = 'chat'  # Изменено с 'register' на 'chat'
        else:
            self.show_error_dialog("Неверный email или пароль")

    def validate_input(self):
        """Проверка введенных данных"""
        if not self.email.text or not self.password.text:
            self.show_error_dialog("Пожалуйста, заполните все поля")
            return False
        return True

    def show_error_dialog(self, text):
        """Показ диалога с ошибкой"""
        dialog = MDDialog(
            title="Ошибка",
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def goto_register(self, instance):
        """Переход на экран регистрации"""
        self.manager.current = 'register'

    def setup_ui(self):
        # Основной контейнер
        main_layout = BoxLayout(orientation='vertical')
        
        # Контейнер для формы
        form_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=min(dp(400), Window.width * 0.9),
            spacing=dp(20),
            padding=dp(20)
        )
        form_container.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        form_container.height = dp(300)
        
        # Заголовок
        from kivymd.uix.label import MDLabel
        title = MDLabel(
            text="Вход в аккаунт",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=dp(50)
        )
        
        # Поля ввода
        self.email = MDTextField(
            hint_text="Email",
            helper_text="Введите email",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(48)
        )
        
        self.password = MDTextField(
            hint_text="Пароль",
            helper_text="Введите пароль",
            helper_text_mode="on_error",
            password=True,
            size_hint_y=None,
            height=dp(48)
        )
        
        # Кнопки
        buttons_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120)
        )
        
        login_button = MDRaisedButton(
            text="Войти",
            on_release=self.login,
            size_hint=(1, None),
            height=dp(50)
        )
        
        register_button = MDRaisedButton(
            text="Регистрация",
            on_release=self.goto_register,
            size_hint=(1, None),
            height=dp(50)
        )
        
        buttons_layout.add_widget(login_button)
        buttons_layout.add_widget(register_button)
        
        # Добавляем все элементы в форму
        form_container.add_widget(title)
        form_container.add_widget(self.email)
        form_container.add_widget(self.password)
        form_container.add_widget(buttons_layout)
        
        # Добавляем форму в основной контейнер
        main_layout.add_widget(form_container)
        
        self.add_widget(main_layout)
    
    def on_window_resize(self, instance, width, height):
        """Обновляем размеры при изменении окна"""
        form_container = self.children[0].children[0]
        form_container.width = min(dp(400), width * 0.9)