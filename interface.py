import os
import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Line
from engine import JutsuTrainerEngine
from widgets import ImageButton
from effects import GifDecoder, AudioManager
from difficulty_widget import DifficultySettingsBlock

LOCAL_KEY_MAP = {
    'q': ('Крыса', 'hand_seals/04_Rat.png'),
    'w': ('Бык', 'hand_seals/09_Ox.png'),
    'e': ('Тигр', 'hand_seals/02_Tiger.png'),
    'r': ('Заяц', 'hand_seals/11_Hare.png'),
    'a': ('Дракон', 'hand_seals/01_Dragon.png'),
    's': ('Змея', 'hand_seals/10_Serpent.png'),
    'd': ('Лошадь', 'hand_seals/06_Horse.png'),
    'f': ('Овца', 'hand_seals/05_Ram.png'),
    'z': ('Обезьяна', 'hand_seals/07_Monkey.png'),
    'x': ('Птица', 'hand_seals/08_Bird.png'),
    'c': ('Собака', 'hand_seals/03_Dog.png'),
    'v': ('Кабан', 'hand_seals/12_Boar.png')
}

class GameInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
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
            _, img_file = LOCAL_KEY_MAP[key]
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

    def _get_current_start_bg(self):
        name = self.engine.current_target_data.get("name", "")
        for fmt in ["jpg", "png"]:
            if "Огненный" in name or "Катон" in name: p = f"hand_seals/katon_start.{fmt}"
            elif "Чидори" in name: p = f"hand_seals/chidori_start.{fmt}"
            elif "Расенган" in name: p = f"hand_seals/rosengan_start.{fmt}"
            elif "Дерева" in name or "Мокутон" in name: p = f"hand_seals/wood_start.{fmt}"
            elif "Теневое" in name or "Клон" in name or "клон" in name: 
                if "Водяное" in name: p = f"hand_seals/water_clone_start.{fmt}"
                else: p = f"hand_seals/clone_start.{fmt}"
            else: return "hand_seals/06_Horse.png"
            
            if os.path.exists(p): 
                return p
        return "hand_seals/06_Horse.png"

    def update_ui(self):
        recipe_hint = " -> ".join([k.upper() for k in self.engine.current_target_key])
        self.target_label.text = f"ТЕХНИКА:\n[b]{self.engine.current_target_data['name']}[/b]\n[size=14sp]Комбо: {recipe_hint}[/size]"
        self.target_label.markup = True
        self.anime_screen.source = self._get_current_start_bg()

    def animate_successful_cast(self, final_chain):
        self.anime_screen.texture = None
        hands_duration = 1.2 
        frame_rate = hands_duration / len(final_chain)
        
        AudioManager.play('sounds/hands.mp3')
        
        for index, key_char in enumerate(final_chain):
            if key_char in LOCAL_KEY_MAP:
                _, img_file = LOCAL_KEY_MAP[key_char]
                Clock.schedule_once(lambda dt, f=img_file: setattr(self.anime_screen, 'source', f) if os.path.exists(f) else None, index * frame_rate)
        
        total_delay = hands_duration + 1.0
        Clock.schedule_once(lambda dt: self.start_real_gif_animation(dict(self.engine.current_target_data)), total_delay)

    def start_real_gif_animation(self, active_data):
        self.anime_screen.source = ''
        self.anime_screen.texture = None
        
        name = active_data.get("name", "")
        if "Чидори" in name: AudioManager.play('sounds/chidori.mp3')
        elif "Огненный" in name or "Катон" in name: AudioManager.play('sounds/katon.mp3')
        elif "Расенган" in name: AudioManager.play('sounds/rosengan.mp3')
        elif "Водяное" in name: AudioManager.play('sounds/water_clone.mp3')
        elif "Дерева" in name or "Мокутон" in name: AudioManager.play('sounds/wood.mp3')
        elif "Клон" in name or "клон" in name: AudioManager.play('sounds/clone.mp3')
            
        gif_frames = GifDecoder.get_frames(active_data.get("effect", ""))
        if gif_frames:
            steps = int(3.0 / 0.08)
            for step in range(steps):
                tex = gif_frames[step % len(gif_frames)]
                Clock.schedule_once(lambda dt, t=tex: self._set_texture_frame(t), step * 0.08)
            Clock.schedule_once(self._next_round, 3.0)
        else:
            self.anime_screen.source = 'atlas://data/images/defaulttheme/slider_tick'
            Clock.schedule_once(self._next_round, 1.5)

    def trigger_error_flash(self):
        AudioManager.play('sounds/error.wav')
        
        def draw_glow_border():
            with self.canvas.after:
                Color(1, 0, 0, 0.2)
                Line(rectangle=(0, 0, Window.width, Window.height), width=24)
                Color(1, 0, 0, 0.5)
                Line(rectangle=(0, 0, Window.width, Window.height), width=14)
                Color(1, 0.2, 0.2, 1)
                Line(rectangle=(0, 0, Window.width, Window.height), width=6)

        def clear_border():
            self.canvas.after.clear()

        def shake_screen(dt):
            self.main_container.pos = (random.randint(-15, 15), random.randint(-15, 15))

        def reset_screen_pos(dt):
            self.main_container.pos = (0, 0)

        for t in [0.0, 0.03, 0.06, 0.09, 0.12, 0.3, 0.33, 0.36, 0.39, 0.42]:
            Clock.schedule_once(shake_screen, t)

        draw_glow_border() 
        Clock.schedule_once(lambda dt: [clear_border(), reset_screen_pos(dt)], 0.18) 
        
        Clock.schedule_once(lambda dt: draw_glow_border(), 0.3)  
        Clock.schedule_once(lambda dt: [clear_border(), reset_screen_pos(dt)], 0.48) 
        
        Clock.schedule_once(self._reset_error_flash, 0.98)

    def _reset_error_flash(self, dt):
        self.engine.generate_new_target()
        self.update_ui()

    def _set_texture_frame(self, texture): 
        self.anime_screen.texture = texture

    def _next_round(self, dt):
        AudioManager.stop_all_effects()
        self.anime_screen.texture = None
        self.engine.generate_new_target()
        self.update_ui()

    def process_input(self, key_char):
        saved_chain = list(self.engine.user_chain) + [key_char]
        status, _, elapsed = self.engine.add_seal(key_char)
        AudioManager.play('sounds/tap.wav')
        if status == "SUCCESS":
            self.status_label.text = f"УСПЕХ за {elapsed:.2f} сек. Каст..."
            Clock.schedule_once(lambda dt: self.animate_successful_cast(saved_chain), 1.0)
        elif status in ["TIMEOUT", "MISCLICK"]:
            self.status_label.text = "Ошибка!"
            self.trigger_error_flash()
        elif status == "PROGRESS":
            self.status_label.text = f"Складывание: {' -> '.join([k.upper() for k in self.engine.user_chain])}"
    def _on_button_press(self, instance): 
        self.process_input(instance.key_id)
        
    def _on_keyboard_down(self, w, key, scancode, codepoint, mod):
        if codepoint and codepoint in LOCAL_KEY_MAP: 
            self.process_input(codepoint)
