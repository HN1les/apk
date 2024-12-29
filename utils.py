from PIL import Image, ImageDraw
import os

def create_default_avatar():
    """Создает аватар по умолчанию, если он не существует"""
    avatar_path = 'assets/default_avatar.png'
    
    # Создаем папку assets, если её нет
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Создаем аватар, только если его нет
    if not os.path.exists(avatar_path):
        # Создаем новое изображение
        size = (200, 200)
        img = Image.new('RGB', size, color='#2196F3')  # Material Blue color
        draw = ImageDraw.Draw(img)
        
        # Рисуем белый круг
        margin = 40
        draw.ellipse(
            [margin, margin, size[0]-margin, size[1]-margin],
            fill='white'
        )
        
        # Сохраняем изображение
        img.save(avatar_path)
    
    return avatar_path