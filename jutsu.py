# jutsu.py
# ~ 15 строк кода
from kivy.app import App
from interface import GameInterface

class JutsuTrainerApp(App):
    def build(self):
        # Название окна (для десктопа)
        self.title = "Jutsu Trainer"
        
        # Просто возвращаем наш кастомный интерфейс
        return GameInterface()

if __name__ == '__main__':
    JutsuTrainerApp().run()
