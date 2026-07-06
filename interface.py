from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from engine import JutsuTrainerEngine
from widgets import ImageButton
from effects import AudioManager
from difficulty_widget import DifficultySettingsBlock

# Подключаем вынесенную логику и карту клавиш из recipes
from interface_logic import InterfaceLogic
from recipes import KEY_MAP

class GameInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Связываем UI с классом логики
        self.logic = InterfaceLogic(self)
        
        self.main_container = BoxLayout(orientation='vertical', padding=15, spacing=8)
        self.add_widget(self.main_container)
        
        self.engine = JutsuTrainerEngine()
        Window.bind(on_key_down=self._on_keyboard_down)
        
        self.anime_screen = Image(source='', size_hint_y=0.4, allow_stretch=True, keep_ratio=False)
        self.main_container.add_widget(self.anime_screen)
        
        self.control_block = DifficultySettingsBlock(self.engine, self.update_ui)
        self.main_container.add_widget(self.control_block)
        
        self.target_label = Label(text="", font_size='22sp', size_hint_y=0.15, halign='center')
        self.main_container.add_widget(self.target_label)
        
        status_row = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        settings_btn = Button(text="ОПЦИИ", font_size='12sp', size_hint_x=0.25, background_color=(0.4, 0.4, 0.4, 1), background_normal='')
        settings_btn.bind(on_press=self._open_settings)
        status_row.add_widget(settings_btn)
        
        self.status_label = Label(text="ДОДЗЁ ОТКРЫТО\nНачните складывать печати!", font_size='16sp', size_hint_x=0.75, halign='center')
        status_row.add_widget(self.status_label)
        
        self.main_container.add_widget(status_row)
        
        buttons_grid = GridLayout(cols=4, spacing=10, size_hint_y=0.3)
        layout_keys = ['q', 'w', 'e', 'r', 'a', 's', 'd', 'f', 'z', 'x', 'c', 'v']
        for key in layout_keys:
            _, img_file = KEY_MAP[key]
            btn = ImageButton(key_id=key, seal_name="", image_path=img_file)
            btn.bind(on_press=self._on_button_press)
            buttons_grid.add_widget(btn)
        self.main_container.add_widget(buttons_grid)
        
        self.update_ui()
        Clock.schedule_once(lambda dt: AudioManager.start_bg_music('sounds/main_theme.mp3'), 0.1)

    def _open_settings(self, instance):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        current_bg_vol = int(AudioManager.get_bg_volume() * 100)
        bg_label = Label(text=f"Громкость музыки: {current_bg_vol}%", font_size='14sp', size_hint_y=None, height=25)
        content.add_widget(bg_label)
        bg_slider = Slider(min=0, max=100, value=current_bg_vol, step=1, size_hint_y=None, height=35)
        bg_slider.bind(value=lambda s, val: [setattr(bg_label, 'text', f"Громкость музыки: {int(val)}%"), AudioManager.set_bg_volume(val / 100.0)])
        content.add_widget(bg_slider)
        
        current_fx_vol = int(AudioManager.get_fx_volume() * 100)
        fx_label = Label(text=f"Громкость эффектов: {current_fx_vol}%", font_size='14sp', size_hint_y=None, height=25)
        content.add_widget(fx_label)
        fx_slider = Slider(min=0, max=100, value=current_fx_vol, step=1, size_hint_y=None, height=35)
        fx_slider.bind(value=lambda s, val: [setattr(fx_label, 'text', f"Громкость эффектов: {int(val)}%"), AudioManager.set_fx_volume(val / 100.0)])
        content.add_widget(fx_slider)
        
        close_btn = Button(text="Закрыть", size_hint_y=None, height=40, background_normal='')
        content.add_widget(close_btn)
        
        popup = Popup(title="Настройки звука", content=content, size_hint=(0.8, 0.55), auto_dismiss=True)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def update_ui(self):
        recipe_hint = " -> ".join([k.upper() for k in self.engine.current_target_key])
        self.target_label.text = f"ТЕХНИКА:\n[b]{self.engine.current_target_data['name']}[/b]\n[size=14sp]Комбо: {recipe_hint}[/size]"
        self.target_label.markup = True
        self.anime_screen.source = self.logic.get_current_start_bg()

    def _on_button_press(self, instance): 
        self.logic.process_input(instance.key_id)
        
    def _on_keyboard_down(self, w, key, scancode, codepoint, mod):
        if codepoint and codepoint in KEY_MAP: 
            self.logic.process_input(codepoint)
