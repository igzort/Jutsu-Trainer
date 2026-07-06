import random
import time
from recipes import NINJUTSU_DATABASE

class JutsuTrainerEngine:
    def __init__(self):
        self.current_target_key = ""
        self.current_target_data = {}
        self.user_chain = []
        self.score = 0
        self.start_time = 0
        self.time_limit = 10.0  # Режим "Чунин" по умолчанию
        
        # Список для псевдорандома (колода доступных техник)
        self.jutsu_pool = []
        
        self.generate_new_target()

    def set_difficulty(self, mode_name: str):
        if mode_name == "Чунин":
            self.time_limit = 10.0
        elif mode_name == "Дзёнин":
            self.time_limit = 4.0
        elif mode_name == "Каге":
            self.time_limit = 1.8
        self.generate_new_target()

    def generate_new_target(self):
        """Выбирает технику по принципу циклического мешка (исключает повторы подряд)."""
        all_keys = list(NINJUTSU_DATABASE.keys())
        
        # Если в базе всего 1 техника, логику проверок применять бессмысленно
        if len(all_keys) <= 1:
            self.current_target_key = all_keys[0] if all_keys else ""
            self.current_target_data = NINJUTSU_DATABASE.get(self.current_target_key, {})
            self.user_chain = []
            self.start_time = time.time()
            return

        # Сохраняем предыдущую технику, чтобы избежать её повторения подряд
        previous_key = self.current_target_key

        # Если мешок пуст, собираем новую колоду и перемешиваем её
        if not self.jutsu_pool:
            self.jutsu_pool = list(all_keys)
            random.shuffle(self.jutsu_pool)
            
            # Если первая техника в новой перемешанной колоде совпадает с прошлой,
            # и в пуле больше 1 элемента, переносим её в конец мешка.
            if self.jutsu_pool[0] == previous_key and len(self.jutsu_pool) > 1:
                first_item = self.jutsu_pool.pop(0)
                self.jutsu_pool.append(first_item)

        # Достаем технику из мешка
        self.current_target_key = self.jutsu_pool.pop(0)
        self.current_target_data = NINJUTSU_DATABASE[self.current_target_key]
        self.user_chain = []
        self.start_time = time.time()

    def add_seal(self, key_char: str) -> tuple:
        self.user_chain.append(key_char)
        current_str = "".join(self.user_chain)
        
        elapsed = time.time() - self.start_time
        if elapsed > self.time_limit:
            self.generate_new_target()
            return "TIMEOUT", None, elapsed

        if current_str == self.current_target_key:
            self.score += 1
            current_name = self.current_target_data["name"]
            self.user_chain = [] 
            return "SUCCESS", current_name, elapsed
            
        if self.current_target_key.startswith(current_str):
            return "PROGRESS", None, elapsed
            
        self.user_chain = []
        return "MISCLICK", None, elapsed
