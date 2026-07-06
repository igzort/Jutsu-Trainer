from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior

class ImageButton(ButtonBehavior, AnchorLayout):
    def __init__(self, key_id, seal_name, image_path, **kwargs):
        super().__init__(**kwargs)
        self.key_id = key_id
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        
        # Сама картинка печати на весь размер кнопки
        img = Image(source=image_path, allow_stretch=True, keep_ratio=False)
        self.add_widget(img)
        
        # Латинская буква строго по центру поверх картинки
        letter_label = Label(
            text=key_id.upper(),
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=2
        )
        self.add_widget(letter_label)
