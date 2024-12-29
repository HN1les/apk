import os
from datetime import datetime
import sqlite3
import shutil
from kivymd.app import MDApp

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('chat.db')
        self.create_tables()

        if not os.path.exists('avatars'):
            os.makedirs('avatars')
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Создаем таблицу пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            avatar_path TEXT DEFAULT NULL,
            bio TEXT DEFAULT ''
        )
        ''')
        
        # Создаем таблицу сообщений
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Добавляем тестового пользователя, если его нет
        cursor.execute('SELECT * FROM users WHERE email = ?', ('test@test.com',))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
            ''', ('test', 'test@test.com', 'test123'))
        
        self.conn.commit()

    def register_user(self, username, email, password):
        """Регистрация нового пользователя"""
        cursor = self.conn.cursor()
        try:
            # Проверяем, существует ли пользователь
            cursor.execute('SELECT * FROM users WHERE email = ? OR username = ?', 
                         (email, username))
            if cursor.fetchone():
                return False, "Пользователь с таким email или именем уже существует"
            
            # Создаем нового пользователя
            cursor.execute('''
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            ''', (username, email, password))
            
            self.conn.commit()
            return True, None
            
        except sqlite3.Error as e:
            return False, f"Ошибка базы данных: {str(e)}"

    def login_user(self, email, password):
        """Вход пользователя"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT id, username, email, avatar_path, bio 
                FROM users 
                WHERE email = ? AND password = ?
            ''', (email, password))
            
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'avatar_path': user[3],
                    'bio': user[4]
                }
            return None
        except Exception as e:
            print(f"Error in login_user: {e}")  # Для отладки
            return None

    def save_message(self, user_id, username, text):
        """Сохранение сообщения"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO messages (user_id, username, text)
            VALUES (?, ?, ?)
        ''', (user_id, username, text))
        self.conn.commit()

    def get_messages(self):
        """Получение сообщений с аватарами"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT m.id, m.user_id, m.username, m.text, m.timestamp, u.avatar_path
            FROM messages m
            LEFT JOIN users u ON m.user_id = u.id
            ORDER BY m.timestamp DESC
            LIMIT 100
        ''')
        
        app = MDApp.get_running_app()
        messages = []
        for row in cursor.fetchall():
            # Используем аватар по умолчанию из приложения
            avatar_path = row[5] if row[5] and os.path.exists(row[5]) else app.default_avatar
            messages.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'text': row[3],
                'timestamp': row[4],
                'avatar_path': avatar_path
            })
        
        return messages

    def update_profile(self, user_id, username=None, bio=None, avatar_path=None):
        """Обновление профиля пользователя"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if username:
            updates.append("username = ?")
            params.append(username)
        if bio is not None:
            updates.append("bio = ?")
            params.append(bio)
        if avatar_path:
            updates.append("avatar_path = ?")
            params.append(avatar_path)
            
        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            params.append(user_id)
            try:
                cursor.execute(query, params)
                self.conn.commit()
                return True, None
            except sqlite3.IntegrityError:
                return False, "Это имя пользователя уже занято"
        return False, "Нет данных для обновления"

    def get_user_profile(self, user_id):
        """Получение профиля пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, username, email, avatar_path, bio 
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'avatar_path': user[3],
                'bio': user[4]
            }
        return None

    def change_password(self, user_id, old_password, new_password):
        """Изменение пароля пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0] == old_password:
            cursor.execute('UPDATE users SET password = ? WHERE id = ?',
                         (new_password, user_id))
            self.conn.commit()
            return True, None
        return False, "Неверный текущий пароль"
    
    def update_avatar(self, user_id, new_avatar_path):
        """Обновление аватара пользователя"""
        try:
            # Получаем текущий аватар
            cursor = self.conn.cursor()
            cursor.execute('SELECT avatar_path FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                # Удаляем старый файл аватара
                old_avatar = result[0]
                if os.path.exists(old_avatar) and 'default_avatar' not in old_avatar:
                    os.remove(old_avatar)
            
            # Обновляем путь к аватару в базе данных
            cursor.execute(
                'UPDATE users SET avatar_path = ? WHERE id = ?',
                (new_avatar_path, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating avatar: {e}")
            return False

    def get_user_avatar(self, user_id):
        """Получение пути к аватару пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT avatar_path FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0] and os.path.exists(result[0]):
            return result[0]
        
        # Возвращаем путь к аватару по умолчанию
        return 'assets/default_avatar.png'

    def get_messages(self):
        """Получение сообщений с аватарами"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT m.id, m.user_id, m.username, m.text, m.timestamp, u.avatar_path
            FROM messages m
            LEFT JOIN users u ON m.user_id = u.id
            ORDER BY m.timestamp DESC
            LIMIT 100
        ''')
        
        messages = []
        for row in cursor.fetchall():
            avatar_path = row[5] if row[5] and os.path.exists(row[5]) else 'assets/default_avatar.png'
            messages.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'text': row[3],
                'timestamp': row[4],
                'avatar_path': avatar_path
            })
        
        return messages