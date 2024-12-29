from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.core.window import Window
import re

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        Window.bind(on_resize=self.on_window_resize)
        
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
        form_container.height = dp(400)  # Увеличенная высота для дополнительного поля
        
        # Заголовок
        from kivymd.uix.label import MDLabel
        title = MDLabel(
            text="Регистрация",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=dp(50)
        )
        
        # Поля ввода
        self.username = MDTextField(
            hint_text="Имя пользователя",
            helper_text="Минимум 3 символа",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(48)
        )
        
        self.email = MDTextField(
            hint_text="Email",
            helper_text="Введите корректный email",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(48)
        )
        
        self.password = MDTextField(
            hint_text="Пароль",
            helper_text="Минимум 6 символов",
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
        
        register_button = MDRaisedButton(
            text="Зарегистрироваться",
            on_release=self.register,
            size_hint=(1, None),
            height=dp(50)
        )
        
        back_button = MDRaisedButton(
            text="Назад",
            on_release=self.goto_login,
            size_hint=(1, None),
            height=dp(50)
        )
        
        buttons_layout.add_widget(register_button)
        buttons_layout.add_widget(back_button)
        
        # Добавляем все элементы в форму
        form_container.add_widget(title)
        form_container.add_widget(self.username)
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

    def register(self, instance):
        """Обработка регистрации пользователя"""
        if not self.validate_input():
            return
            
        app = MDApp.get_running_app()
        success, error = app.db.register_user(
            username=self.username.text,
            email=self.email.text,
            password=self.password.text
        )
        
        if success:
            self.show_success_dialog()
        else:
            self.show_error_dialog(error)

    def validate_input(self):
        """Проверка введенных данных"""
        if not self.username.text or not self.email.text or not self.password.text:
            self.show_error_dialog("Пожалуйста, заполните все поля")
            return False
            
        if len(self.username.text) < 3:
            self.show_error_dialog("Имя пользователя должно содержать минимум 3 символа")
            return False
            
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, self.email.text):
            self.show_error_dialog("Неверный формат email")
            return False
            
        if len(self.password.text) < 6:
            self.show_error_dialog("Пароль должен содержать минимум 6 символов")
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

    def show_success_dialog(self):
        """Показ диалога успешной регистрации"""
        dialog = MDDialog(
            title="Успех",
            text="Регистрация успешна! Теперь вы можете войти.",
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: self.handle_success_dialog(x, dialog)
                )
            ]
        )
        dialog.open()

    def handle_success_dialog(self, instance, dialog):
        """Обработка закрытия диалога успешной регистрации"""
        dialog.dismiss()
        self.goto_login(None)

    def goto_login(self, instance):
        """Переход на экран входа"""
        self.manager.current = 'login'