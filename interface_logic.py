import os
import random
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from effects import GifDecoder, AudioManager
from recipes import KEY_MAP

class InterfaceLogic:
    def __init__(self, view_component):
        self.view = view_component  # Ссылка на Kivy UI для управления экраном

    def get_current_start_bg(self):
        name = self.view.engine.current_target_data.get("name", "")
        for fmt in ["jpg", "png"]:
            if "Огненный" in name or "Катон" in name:
                p = f"hand_seals/katon_start.{fmt}"
            elif "Чидори" in name:
                p = f"hand_seals/chidori_start.{fmt}"
            elif "Расенган" in name:
                p = f"hand_seals/rosengan_start.{fmt}"
            elif "Дерева" in name or "Мокутон" in name:
                p = f"hand_seals/wood_start.{fmt}"
            elif "Шинра" in name:
                p = f"hand_seals/shinra_start.{fmt}"
            elif "Сюрикен" in name or "Расен Сюрикен" in name:
                p = f"hand_seals/suriken_start.{fmt}"
            elif "Теневое" in name or "Клон" in name or "клон" in name:
                if "Водяное" in name:
                    p = f"hand_seals/water_clone_start.{fmt}"
                else:
                    p = f"hand_seals/clone_start.{fmt}"
            else:
                return "hand_seals/06_Horse.png"
            if os.path.exists(p):
                return p
        return "hand_seals/06_Horse.png"

    def animate_successful_cast(self, final_chain):
        self.view.anime_screen.texture = None
        hands_duration = 1.2
        frame_rate = hands_duration / len(final_chain)
        
        AudioManager.play('sounds/hands.mp3')
        
        for index, key_char in enumerate(final_chain):
            if key_char in KEY_MAP:
                _, img_file = KEY_MAP[key_char]
                Clock.schedule_once(lambda dt, f=img_file: setattr(self.view.anime_screen, 'source', f) if os.path.exists(f) else None, index * frame_rate)
        
        total_delay = hands_duration + 1.0
        Clock.schedule_once(lambda dt: self.start_real_gif_animation(dict(self.view.engine.current_target_data)), total_delay)

    def start_real_gif_animation(self, active_data):
        self.view.anime_screen.source = ''
        self.view.anime_screen.texture = None
        
        name = active_data.get("name", "")
        
        # Стандартный мгновенный запуск звуков
        if "Чидори" in name:
            AudioManager.play('sounds/chidori.mp3')
        elif "Огненный" in name or "Катон" in name:
            AudioManager.play('sounds/katon.mp3')
        elif "Расенган" in name:
            AudioManager.play('sounds/rosengan.mp3')
        elif "Водяное" in name:
            AudioManager.play('sounds/water_clone.mp3')
        elif "Дерева" in name or "Мокутон" in name:
            AudioManager.play('sounds/wood.mp3')
        elif "Сюрикен" in name or "Расен Сюрикен" in name:
            AudioManager.play('sounds/suriken.mp3')
        elif "Шинра" in name:
            AudioManager.play('sounds/shinra1.mp3')
            Clock.schedule_once(lambda dt: AudioManager.play('sounds/shinra2.mp3'), 2.0)
        elif "Клон" in name or "клон" in name:
            AudioManager.play('sounds/clone.mp3')
            
        gif_frames = GifDecoder.get_frames(active_data.get("effect", ""))
        if gif_frames:
            # Сюрикен теперь идет строго 3.0 секунды, как и Чидори с Расенганом!
            duration = 4.0 if "Шинра" in name else 3.0
                
            steps = int(duration / 0.08)
            for step in range(steps):
                tex = gif_frames[step % len(gif_frames)]
                Clock.schedule_once(lambda dt, t=tex: setattr(self.view.anime_screen, 'texture', t), step * 0.08)
            Clock.schedule_once(self.next_round, duration)
        else:
            self.view.anime_screen.source = 'atlas://data/images/defaulttheme/slider_tick'
            Clock.schedule_once(self.next_round, 1.5)

    def trigger_error_flash(self):
        AudioManager.play('sounds/error.wav')
        
        def draw_glow_border():
            with self.view.canvas.after:
                Color(1, 0, 0, 0.2)
                Line(rectangle=(0, 0, Window.width, Window.height), width=24)
                Color(1, 0, 0, 0.5)
                Line(rectangle=(0, 0, Window.width, Window.height), width=14)
                Color(1, 0.2, 0.2, 1)
                Line(rectangle=(0, 0, Window.width, Window.height), width=6)

        def clear_border():
            self.view.canvas.after.clear()

        def shake_screen(dt):
            self.view.main_container.pos = (random.randint(-15, 15), random.randint(-15, 15))

        def reset_screen_pos(dt):
            self.view.main_container.pos = (0, 0)

        draw_glow_border()
        shake_event = Clock.schedule_interval(shake_screen, 0.3)
        
        Clock.schedule_once(lambda dt: [clear_border(), shake_event.cancel(), reset_screen_pos(dt)], 0.48)
        Clock.schedule_once(self.reset_error_flash, 0.98)

    def reset_error_flash(self, dt):
        self.view.engine.generate_new_target()
        self.view.update_ui()

    def next_round(self, dt):
        # Мягкое глушение затянувшихся хвостов через 0.5 сек после раунда
        Clock.schedule_once(lambda d: AudioManager.stop_all_effects(), 0.5)
        
        self.view.anime_screen.texture = None
        self.view.engine.generate_new_target()
        self.view.update_ui()

    def process_input(self, key_char):
        saved_chain = list(self.view.engine.user_chain) + [key_char]
        status, _, elapsed = self.view.engine.add_seal(key_char)
        AudioManager.play('sounds/tap.wav')
        if status == "SUCCESS":
            self.view.status_label.text = f"УСПЕХ за {elapsed:.2f} сек. Каст..."
            Clock.schedule_once(lambda dt: self.animate_successful_cast(saved_chain), 1.0)
        elif status in ["TIMEOUT", "MISCLICK"]:
            self.view.status_label.text = "Ошибка!"
            self.trigger_error_flash()
        elif status == "PROGRESS":
            self.view.status_label.text = f"Складывание: {' -> '.join([k.upper() for k in self.view.engine.user_chain])}"
