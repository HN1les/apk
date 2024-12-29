from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.metrics import dp
from plyer import filechooser
import shutil
from kivy.uix.image import AsyncImage
import os

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        # Верхняя панель
        self.toolbar = MDTopAppBar(
            title="Профиль",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["content-save", lambda x: self.save_profile()]]
        )
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Аватар
        avatar_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            spacing=10
        )
        
        # Используем аватар из приложения
        app = MDApp.get_running_app()
        self.avatar_image = AsyncImage(
            source=app.default_avatar,  # Используем аватар из приложения
            size_hint=(None, None),
            size=(dp(150), dp(150)),
            fit_mode="cover",
            pos_hint={'center_x': 0.5}
        )
        
        change_avatar_button = MDFlatButton(
            text="Изменить аватар",
            on_release=self.choose_avatar,
            pos_hint={'center_x': 0.5}
        )
        
        avatar_layout.add_widget(self.avatar_image)
        avatar_layout.add_widget(change_avatar_button)
        
        # Поля профиля
        self.username = MDTextField(
            hint_text="Имя пользователя",
            helper_text="Минимум 3 символа",
            helper_text_mode="on_error"
        )
        
        self.bio = MDTextField(
            hint_text="О себе",
            multiline=True,
            max_height=dp(100)
        )
        
        # Кнопка смены пароля
        change_password_button = MDRaisedButton(
            text="Сменить пароль",
            on_release=self.show_change_password_dialog,
            pos_hint={'center_x': 0.5}
        )
        
        # Добавляем все элементы
        content.add_widget(avatar_layout)
        content.add_widget(self.username)
        content.add_widget(self.bio)
        content.add_widget(change_password_button)
        
        layout.add_widget(self.toolbar)
        layout.add_widget(content)
        
        self.add_widget(layout)
        
    def on_enter(self):
        """Загружаем данные профиля при входе на экран"""
        app = MDApp.get_running_app()
        if not hasattr(app, 'current_user'):
            self.manager.current = 'login'
            return
            
        profile = app.db.get_user_profile(app.current_user['id'])
        if profile:
            self.username.text = profile['username']
            self.bio.text = profile['bio'] or ""
            if profile['avatar_path']:
                self.avatar_image.source = profile['avatar_path']

    def choose_avatar(self, instance):
        """Выбор нового аватара"""
        try:
            filechooser.open_file(
                on_selection=self.handle_avatar_selection,
                filters=['*.png', '*.jpg', '*.jpeg']
            )
        except Exception as e:
            self.show_error_dialog(f"Ошибка при выборе файла: {str(e)}")

    def handle_avatar_selection(self, selection):
        """Обработка выбора аватара"""
        if not selection:
            return
            
        file_path = selection[0]
        
        # Создаем папку avatars, если её нет
        if not os.path.exists('avatars'):
            os.makedirs('avatars')
        
        app = MDApp.get_running_app()
        # Получаем расширение файла
        file_extension = os.path.splitext(file_path)[1].lower()
        # Проверяем, что это изображение
        if file_extension not in ['.png', '.jpg', '.jpeg']:
            self.show_error_dialog("Пожалуйста, выберите изображение (PNG, JPG)")
            return
            
        new_path = f'avatars/user_{app.current_user["id"]}{file_extension}'
        
        try:
            # Копируем файл
            shutil.copy2(file_path, new_path)
            # Обновляем путь к аватару в базе данных
            app.db.update_profile(
                user_id=app.current_user['id'],
                avatar_path=new_path
            )
            # Обновляем отображение
            self.avatar_image.source = new_path
            # Перезагружаем изображение
            self.avatar_image.reload()
        except Exception as e:
            self.show_error_dialog(f"Ошибка при сохранении аватара: {str(e)}")

    def save_profile(self):
        """Сохраняем изменения профиля"""
        app = MDApp.get_running_app()
        success, error = app.db.update_profile(
            user_id=app.current_user['id'],
            username=self.username.text,
            bio=self.bio.text,
            avatar_path=self.avatar_image.source
        )
        
        if success:
            app.current_user['username'] = self.username.text
            self.show_success_dialog("Профиль успешно обновлен")
        else:
            self.show_error_dialog(error)

    def show_change_password_dialog(self, instance):
        """Показываем диалог смены пароля"""
        self.password_dialog = MDDialog(
            title="Изменение пароля",
            type="custom",
            content_cls=ChangePasswordContent(),
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    on_release=lambda x: self.password_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="СОХРАНИТЬ",
                    on_release=self.change_password
                ),
            ],
        )
        self.password_dialog.open()

    def change_password(self, instance):
        """Меняем пароль"""
        content = self.password_dialog.content_cls
        if not content.old_password.text or not content.new_password.text:
            self.show_error_dialog("Заполните все поля")
            return
            
        if content.new_password.text != content.confirm_password.text:
            self.show_error_dialog("Новые пароли не совпадают")
            return
            
        app = MDApp.get_running_app()
        success, error = app.db.change_password(
            app.current_user['id'],
            content.old_password.text,
            content.new_password.text
        )
        
        if success:
            self.password_dialog.dismiss()
            self.show_success_dialog("Пароль успешно изменен")
        else:
            self.show_error_dialog(error)

    def show_error_dialog(self, text):
        dialog = MDDialog(
            title="Ошибка",
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )
        dialog.open()

    def show_success_dialog(self, text):
        dialog = MDDialog(
            title="Успех",
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )
        dialog.open()

    def go_back(self):
        self.manager.current = 'chat'

class ChangePasswordContent(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.size_hint_y = None
        self.height = 180
        
        self.old_password = MDTextField(
            hint_text="Текущий пароль",
            password=True
        )
        self.new_password = MDTextField(
            hint_text="Новый пароль",
            password=True
        )
        self.confirm_password = MDTextField(
            hint_text="Подтвердите новый пароль",
            password=True
        )
        
        self.add_widget(self.old_password)
        self.add_widget(self.new_password)
        self.add_widget(self.confirm_password)