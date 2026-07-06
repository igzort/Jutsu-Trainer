from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class DifficultySettingsBlock(BoxLayout):
    def __init__(self, engine, update_ui_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 40
        self.spacing = 10
        
        self.engine = engine
        self.update_ui_callback = update_ui_callback
        self.diff_buttons = {}

        # Только кнопки сложности, без опций
        modes = [("Чунин", (0.2, 0.7, 0.3, 1)), ("Дзёнин", (0.2, 0.5, 0.8, 1)), ("Каге", (0.8, 0.2, 0.2, 1))]
        
        for mode_name, btn_color in modes:
            diff_btn = Button(
                text=mode_name, 
                font_size='14sp', 
                background_color=btn_color,
                background_normal='', # Дефолтное состояние
                background_down=''    # Текстура для вжатого состояния
            )
            diff_btn.bind(on_press=self._change_difficulty)
            self.add_widget(diff_btn)
            self.diff_buttons[mode_name] = (diff_btn, btn_color)
            
        self.highlight_active_difficulty("Чунин")

    def highlight_active_difficulty(self, active_mode):
        """Активная кнопка визуально утапливается назад, неактивные становятся выпуклыми"""
        for mode_name, (btn, def_color) in self.diff_buttons.items():
            if mode_name == active_mode:
                btn.background_color = (1.0, 0.84, 0.0, 1) # Золотой цвет
                btn.text = f"• {mode_name} •"
                # Подменяем текстуру нормального состояния на текстуру нажатого (кнопка кажется вжатой)
                btn.background_normal = btn.background_down 
            else:
                btn.background_color = def_color
                btn.text = mode_name
                btn.background_normal = '' # Возвращаем обычный выпуклый вид

    def _change_difficulty(self, instance):
        mode = instance.text.replace("•", "").strip()
        self.engine.set_difficulty(mode)
        self.highlight_active_difficulty(mode)
        self.update_ui_callback()
