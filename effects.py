import os
import io
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
from recipes import KEY_MAP

try:
    from PIL import Image as PILImage, ImageSequence
except ImportError:
    pass

class GifDecoder:
    @staticmethod
    def get_frames(gif_path):
        if not os.path.exists(gif_path): return []
        try:
            im = PILImage.open(gif_path)
            frames = []
            for frame in ImageSequence.Iterator(im):
                buf = io.BytesIO()
                frame.convert('RGBA').save(buf, format='png')
                buf.seek(0)
                frames.append(CoreImage(buf, ext='png').texture)
            return frames
        except: return []

class AudioManager:
    _bg_music = None
    _fx_volume = 1.0
    _active_sounds = []

    @staticmethod
    def play(sound_file):
        """Играет звуковой эффект с текущей громкостью эффектов"""
        if os.path.exists(sound_file):
            try:
                sound = SoundLoader.load(sound_file)
                if sound:
                    sound.volume = AudioManager._fx_volume
                    # Очищаем мертвые звуки из списка перед добавлением нового
                    AudioManager._active_sounds = [s for s in AudioManager._active_sounds if s.state == 'play']
                    AudioManager._active_sounds.append(sound)
                    sound.play()
            except: pass

    @staticmethod
    def stop_all_effects():
        """Принудительно обрывает все играющие в данный момент эффекты"""
        for sound in AudioManager._active_sounds:
            try: sound.stop()
            except: pass
        AudioManager._active_sounds.clear()

    @staticmethod
    def start_bg_music(music_file):
        if os.path.exists(music_file):
            try:
                if AudioManager._bg_music: return
                AudioManager._bg_music = SoundLoader.load(music_file)
                if AudioManager._bg_music:
                    AudioManager._bg_music.loop = True
                    AudioManager._bg_music.play()
            except: pass

    @staticmethod
    def set_bg_volume(volume):
        if AudioManager._bg_music: AudioManager._bg_music.volume = volume

    @staticmethod
    def get_bg_volume():
        if AudioManager._bg_music: return AudioManager._bg_music.volume
        return 1.0

    @staticmethod
    def set_fx_volume(volume):
        """Меняет громкость для будущих эффектов"""
        AudioManager._fx_volume = volume

    @staticmethod
    def get_fx_volume():
        return AudioManager._fx_volume
