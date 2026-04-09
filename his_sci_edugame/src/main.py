import pygame
import sys
import random
import json
import os
import math
from enum import Enum

def _get_base_path():
    """获取资源根目录，支持 PyInstaller 打包运行。"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def _get_questions_path():
    """获取题目目录，兼容 .app 同级及 Application Support 获取，或编辑器项目"""
    if getattr(sys, 'frozen', False):

        app_bundle = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        app_dir = os.path.dirname(app_bundle)
        path_next_to_app = os.path.join(app_dir, 'questions')
        path_in_support = os.path.expanduser('~/Library/Application Support/HisSciEdugame/questions')

        if os.path.isdir(path_next_to_app):
            return path_next_to_app
        os.makedirs(path_in_support, exist_ok=True)
        return path_in_support

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions')

def _get_audio_path():
    """获取音频目录，包括背景音乐等。"""
    if getattr(sys, 'frozen', False):
        app_bundle = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        app_dir = os.path.dirname(app_bundle)
        path_next_to_app = os.path.join(app_dir, 'audio')
        if os.path.isdir(path_next_to_app):
            return path_next_to_app
        return os.path.join(os.path.expanduser('~/Library/Application Support/HisSciEdugame'), 'audio')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')

def _get_data_path():
    """获取可写数据目录，排行榜等，优先使用用户目录。"""
    if getattr(sys, 'frozen', False):
        base = os.path.expanduser('~/Library/Application Support/HisSciEdugame')
        os.makedirs(base, exist_ok=True)
        return base
    return os.path.dirname(os.path.abspath(__file__))

from typing import List, Dict, Tuple, Optional
from questions import ScienceQuestions, Question, Difficulty
from leaderboard import Leaderboard
try:
    from audio_utils import init_audio, play_sound, play_music, stop_music
except ImportError:
    def init_audio(): return False
    def play_sound(_): return False
    def play_music(*_, **__): return False
    def stop_music(): return None

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 255, 150)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (200, 220, 255)
MC_GRASS = (124, 189, 107)
MC_DIRT = (134, 96, 67)
MC_STONE = (125, 125, 125)
MC_SKY = (113, 197, 207)
MC_WOOD = (157, 128, 79)
MC_STEVE_SKIN = (255, 219, 172)
MC_STEVE_SHIRT = (21, 119, 136)
MC_STEVE_PANTS = (30, 30, 135)
MC_NETHER = (100, 20, 20)
MC_NETHERRACK = (139, 69, 19)
MC_LAVA = (255, 100, 0)

MC_END_STONE = (220, 220, 160)
MC_END_SKY = (20, 10, 30)
MC_PURPLE = (128, 0, 128)

SAND = (237, 201, 175)
SAND_DARK = (210, 180, 140)
SNOW = (240, 248, 255)
SNOW_DIRT = (200, 210, 220)

ALPINE_STONE = (140, 140, 150)
ALPINE_SNOW = (240, 248, 255)
OCEAN_BLUE = (30, 100, 180)
OCEAN_DEEP = (20, 60, 120)
BADLANDS_TERRACOTTA = (180, 100, 60)
BADLANDS_ORANGE = (210, 130, 70)

class GameState(Enum):
    MENU = 1
    NAME_INPUT = 2
    OVERWORLD = 3
    NETHER = 4
    END = 5
    QUESTION = 6
    FEEDBACK = 7
    RESULTS = 8
    LEADERBOARD = 9

class ScienceGame:
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        init_audio()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Science Adventure - Learn & Play!')
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 24)

        self.state = GameState.MENU
        self.questions = ScienceQuestions(_get_questions_path())
        self.current_question = None
        self.current_answers = []
        self.selected_answer = None
        self.score = 0
        self.streak = 0
        self.wrong_count = 0
        self.questions_answered = 0
        self.difficulty_level = Difficulty.EASY
        self.time_limit = 0
        self.time_remaining = 0
        self.question_start_time = 0
        self.question_elapsed_time = 0

        self.health = 10
        self.max_health = 10
        self.obsidian_count = 0
        self.ender_pearl_count = 0
        self.blaze_rod_count = 0
        self.bread_count = 0
        self.golden_apple_count = 0
        self.totem_count = 0
        self.in_question = False
        self.total_questions = 20
        self.world_start_time = 0

        self.player_x = SCREEN_WIDTH // 2
        self.player_speed = 8

        self.ground_y = SCREEN_HEIGHT - 200
        self.player_y = float(self.ground_y)
        self.player_vy = 0.0
        self.gravity = 1.0
        self.jump_vy = -18.0
        self.on_ground = True
        self.current_world = 'overworld'

        self.biomes = ['forest', 'plains', 'desert', 'snow', 'alpine', 'ocean', 'badlands']
        self.current_biome = 'forest'

        self._fall_peak_y = None

        self.alpine_platforms = []

        self._biome_enter_time = 0
        self._badlands_last_damage_time = 0

        self._hurt_flash_until = 0

        self.map_seed = random.randint(0, 10000)
        self.map_changes = 0

        self.overworld_tree_hits = set()
        self.overworld_cactus_hits = set()

        self.overworld_items = []
        self.last_item_spawn_time = 0
        self.item_spawn_interval = 10000
        self.item_lifetime = 1000
        self.question_start_item_time = 0

        self.piglin_fortress_questions = 0
        self.nether_fortress_questions = 0

        self.end_crystal_questions = []
        self.end_crystal_answered = []
        self.end_crystal_failed = []
        self.end_crystal_count = 5
        self._current_crystal_id = None
        self.feedback_message = ''
        self.feedback_color = WHITE
        self.feedback_timer = 0
        self.is_answer_correct = False
        self.waiting_for_esc = False
        self.show_return_to_lobby_prompt = False

        self.topics = ['water_cycle', 'states_of_matter', 'solar_system', 'plants', 'animals']
        self.current_topic = None

        self.player_name = ''
        self.name_input_text = ''
        self.name_input_active = False

        _data_dir = _get_data_path()
        self.leaderboard = Leaderboard(os.path.join(_data_dir, 'leaderboard.json'))
        self._lobby_music_started = False

        self.image_cache = {}

    def _start_lobby_music(self):
        """播放大厅 C418 Minecraft Volume Alpha 背景音乐。"""
        if self._lobby_music_started:
            return
        audio_dir = _get_audio_path()
        music_file = os.path.join(audio_dir, 'C418 - Minecraft - Minecraft Volume Alpha 4.mp3')
        if play_music(music_file, loop=-1, volume=0.4):
            self._lobby_music_started = True
        else:
            self._lobby_music_started = True

    def _stop_lobby_music(self):
        """停止大厅音乐。"""
        stop_music()
        self._lobby_music_started = False

    def _start_game_music(self):
        """游戏正式开始后播放 Subwoofer Lullaby 背景音乐。"""
        audio_dir = _get_audio_path()
        music_file = os.path.join(audio_dir, 'C418 - Subwoofer Lullaby - Minecraft Volume Alpha 4.mp3')
        play_music(music_file, loop=-1, volume=0.4)

    def _load_image(self, image_path: str) -> Optional[pygame.Surface]:
        """
        Load an image with caching.

        Args:
            image_path: Path to the image file

        Returns:
            pygame.Surface if image loads successfully, None otherwise
        """
        if not image_path:
            return None

        if image_path in self.image_cache:
            return self.image_cache[image_path]

        try:
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                self.image_cache[image_path] = image
                return image
            else:
                print(f"Warning: Image not found: {image_path}")
                return None
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def handle_menu_events(self, event):
        """Handle events in the menu state"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if 400 <= mouse_pos[0] <= 800 and 230 <= mouse_pos[1] <= 300:
                play_sound('click')
                self.state = GameState.NAME_INPUT
                self.name_input_text = self.player_name if self.player_name else ''
                self.name_input_active = True
            elif 400 <= mouse_pos[0] <= 800 and 315 <= mouse_pos[1] <= 370:
                play_sound('click')
                self.state = GameState.LEADERBOARD
            for i, topic in enumerate(self.topics):
                y_pos = 420 + i * 58
                if 400 <= mouse_pos[0] <= 800 and y_pos <= mouse_pos[1] <= y_pos + 48:
                    play_sound('click')
                    self.current_topic = topic
                    self.state = GameState.NAME_INPUT
                    self.name_input_text = self.player_name if self.player_name else ''
                    self.name_input_active = True

    def start_game(self):
        """Initialize a new game session"""
        self._stop_lobby_music()
        self._start_game_music()
        if self.name_input_text.strip():
            self.player_name = self.name_input_text.strip()
        elif not self.player_name:
            self.player_name = 'Player'

        self.state = GameState.OVERWORLD
        self.score = 0
        self.streak = 0
        self.wrong_count = 0
        self.questions_answered = 0
        self.difficulty_level = Difficulty.EASY
        self.is_answer_correct = False
        self.waiting_for_esc = False
        self._score_saved = False
        self.health = 10
        self.max_health = 10
        self.in_question = False
        self.question_elapsed_time = 0

        self.obsidian_count = 0
        self.ender_pearl_count = 0
        self.blaze_rod_count = 0
        self.bread_count = 0
        self.golden_apple_count = 0
        self.totem_count = 0

        self.current_world = 'overworld'
        self.current_biome = 'forest'
        self._fall_peak_y = None
        self._biome_enter_time = pygame.time.get_ticks()
        self._badlands_last_damage_time = 0
        self._hurt_flash_until = 0
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = float(self.ground_y)
        self.player_vy = 0.0
        self.on_ground = True
        self.overworld_tree_hits = set()
        self.overworld_cactus_hits = set()
        self.map_seed = random.randint(0, 10000)
        self.map_changes = 0
        self.piglin_fortress_questions = 0
        self.nether_fortress_questions = 0
        self.end_crystal_answered = []
        self.end_crystal_failed = []
        self._last_map_check_x = self.player_x
        self.world_start_time = pygame.time.get_ticks()
        self._init_end_crystals()

        self.overworld_items = []
        self.last_item_spawn_time = pygame.time.get_ticks()

    def load_next_question(self):
        """Load a new question based on current difficulty"""
        if self.current_topic:
            self.current_question = self.questions.get_question_by_topic(
                self.current_topic, self.difficulty_level)
        else:
            self.current_question = self.questions.get_random_question(
                self.difficulty_level)

        if self.current_question:

            self.current_answers = self.current_question.answers.copy()
            random.shuffle(self.current_answers)
            self.selected_answer = None
            self.question_start_time = pygame.time.get_ticks()
            self.question_elapsed_time = 0
            self.state = GameState.QUESTION
            self.in_question = True

            if self.current_world == 'overworld':
                current_time = pygame.time.get_ticks()
                elapsed_since_last_spawn = current_time - self.last_item_spawn_time
                self.question_start_item_time = elapsed_since_last_spawn

    def check_answer(self, answer_index: int):
        """Check if the selected answer is correct"""
        if not self.current_question:
            return

        selected_text = self.current_answers[answer_index]
        is_correct = selected_text == self.current_question.correct_answer

        self.questions_answered += 1
        self.state = GameState.FEEDBACK
        self.feedback_timer = pygame.time.get_ticks()

        elapsed = (pygame.time.get_ticks() - self.question_start_time) / 1000
        time_bonus = 0

        if is_correct:
            play_sound('correct')
            self.is_answer_correct = True
            self.waiting_for_esc = False
            self.streak += 1
            self.wrong_count = 0
            points = 100 + time_bonus + self.streak * 10
            self.score += points

            if self.current_world == 'overworld':
                self.obsidian_count += 1
                self.feedback_message = f"Correct! +{points} points! +1 Obsidian! (Streak: {self.streak})"
            elif self.current_world == 'nether':
                if self.player_x < SCREEN_WIDTH // 2:
                    self.ender_pearl_count += 1
                    self.piglin_fortress_questions += 1
                    self.feedback_message = f"Correct! +1 Ender Pearl! ({self.ender_pearl_count}/3)"
                else:
                    self.blaze_rod_count += 1
                    self.nether_fortress_questions += 1
                    self.feedback_message = f"Correct! +1 Blaze Rod! ({self.blaze_rod_count}/3)"
            elif self.current_world == 'end':

                crystal_id = self._current_crystal_id
                if crystal_id is not None:
                    if not isinstance(self.end_crystal_answered, list):
                        self.end_crystal_answered = []
                    if crystal_id not in self.end_crystal_answered:
                        self.end_crystal_answered.append(crystal_id)
                    if isinstance(self.end_crystal_failed, list) and crystal_id in self.end_crystal_failed:
                        self.end_crystal_failed.remove(crystal_id)
                self.feedback_message = f"Correct! End Crystal destroyed! ({len(self.end_crystal_answered)}/{self.end_crystal_count})"

            self.feedback_color = GREEN

            if self.streak % 4 == 0 and self.streak > 0 and self.difficulty_level != Difficulty.HARD:
                if self.difficulty_level == Difficulty.EASY:
                    self.difficulty_level = Difficulty.MEDIUM
                elif self.difficulty_level == Difficulty.MEDIUM:
                    self.difficulty_level = Difficulty.HARD
                self.feedback_message += "\nDifficulty increased!"

        else:
            play_sound('wrong')
            self.is_answer_correct = False
            self.waiting_for_esc = True
            self.streak = 0
            self.wrong_count += 1

            health_loss = 1
            if self.current_world == 'overworld':
                health_loss = 1
            elif self.current_world == 'nether':
                if self.player_x < SCREEN_WIDTH // 2:
                    health_loss = 3
                else:
                    health_loss = 2
            elif self.current_world == 'end':
                crystal_id = self._current_crystal_id
                if crystal_id is not None and crystal_id in self.end_crystal_failed:
                    health_loss = 4
                else:
                    health_loss = 3
                    if crystal_id is not None:
                        if not isinstance(self.end_crystal_failed, list):
                            self.end_crystal_failed = []
                        self.end_crystal_failed.append(crystal_id)

            if self.health - health_loss <= 0 and self.totem_count > 0:
                self.totem_count -= 1
                self.health = 5
                play_sound('totem')
                self.feedback_message = "Totem of Undying activated! Revived with 5 hearts!"
            else:
                self.health = max(0, self.health - health_loss)

            correct_answer = self.current_question.correct_answer
            explanation = self.current_question.explanation or ''
            self.feedback_message = f"Incorrect. The correct answer is: {correct_answer}"
            if explanation:
                self.feedback_message += f"\n\nExplanation: {explanation}"
            self.feedback_message += f"\n\n-{health_loss} Heart(s)! Press ESC to continue..."
            self.feedback_color = RED

            if self.wrong_count >= 1 and self.difficulty_level != Difficulty.EASY:
                if self.difficulty_level == Difficulty.HARD:
                    self.difficulty_level = Difficulty.MEDIUM
                elif self.difficulty_level == Difficulty.MEDIUM:
                    self.difficulty_level = Difficulty.EASY
                self.feedback_message = self.feedback_message.replace("\n\nPress ESC to continue...", "")
                self.feedback_message += "\nDifficulty decreased.\n\nPress ESC to continue..."
                self.wrong_count = 0

    def handle_question_events(self, event):
        """Handle events during question state"""
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1 and len(self.current_answers) > 0:
                self.selected_answer = 0
                self.check_answer(0)

            elif event.key == pygame.K_2 and len(self.current_answers) > 1:
                self.selected_answer = 1
                self.check_answer(1)

            elif event.key == pygame.K_3 and len(self.current_answers) > 2:
                self.selected_answer = 2
                self.check_answer(2)

            elif event.key == pygame.K_4 and len(self.current_answers) > 3:
                self.selected_answer = 3
                self.check_answer(3)

            elif event.key == pygame.K_ESCAPE:
                if self.current_world == "overworld":
                    self.state = GameState.OVERWORLD
                elif self.current_world == "nether":
                    self.state = GameState.NETHER
                elif self.current_world == "end":
                    self.state = GameState.END

                self.in_question = False
                self.question_start_time = 0
                self.question_elapsed_time = 0

                if self.current_world == "overworld":
                    current_time = pygame.time.get_ticks()
                    self.last_item_spawn_time = current_time - self.question_start_item_time

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                mouse_pos = event.pos

                for i in range(len(self.current_answers)):
                    answer_rect = self._get_answer_rect(i)
                    if answer_rect and answer_rect.collidepoint(mouse_pos):
                        play_sound("click")
                        self.selected_answer = i
                        self.check_answer(i)
                        break

    def handle_overworld_events(self, event):
        """Handle events in Overworld"""
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_q:
                if not self.in_question:
                    self.difficulty_level = Difficulty.EASY
                    self.load_next_question()
                    self.in_question = True

            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if not self.in_question and self.on_ground:
                    play_sound("jump")
                    self.player_vy = self.jump_vy
                    self.on_ground = False

            elif event.key == pygame.K_1 and self.bread_count > 0:
                self.bread_count -= 1
                self.health = min(self.max_health, self.health + 1)
                play_sound("heal")

            elif event.key == pygame.K_2 and self.golden_apple_count > 0:
                self.golden_apple_count -= 1
                self.health = min(self.max_health, self.health + 3)
                play_sound("heal")

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 3:
                if self.obsidian_count >= 5:
                    self.obsidian_count -= 5
                    self.state = GameState.NETHER
                    self.current_world = "nether"
                    self.player_x = SCREEN_WIDTH // 2
                    self.player_y = float(self.ground_y)
                    self.player_vy = 0.0
                    self.on_ground = True
                    self.piglin_fortress_questions = 0
                    self.nether_fortress_questions = 0

    def handle_nether_events(self, event):
        """Handle events in Nether"""
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_q:
                if not self.in_question:
                    if self.player_x < SCREEN_WIDTH // 2:
                        if self.piglin_fortress_questions < 3:
                            self.difficulty_level = Difficulty.MEDIUM
                            self.load_next_question()
                            self.in_question = True
                    else:
                        if self.nether_fortress_questions < 3:
                            self.difficulty_level = Difficulty.EASY
                            self.load_next_question()
                            self.in_question = True

            elif event.key == pygame.K_1 and self.bread_count > 0:
                self.bread_count -= 1
                self.health = min(self.max_health, self.health + 1)
                play_sound("heal")

            elif event.key == pygame.K_2 and self.golden_apple_count > 0:
                self.golden_apple_count -= 1
                self.health = min(self.max_health, self.health + 3)
                play_sound("heal")

            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if not self.in_question and self.on_ground:
                    play_sound("jump")
                    self.player_vy = self.jump_vy
                    self.on_ground = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 3:
                if self.ender_pearl_count >= 3 and self.blaze_rod_count >= 3:
                    self.ender_pearl_count -= 3
                    self.blaze_rod_count -= 3
                    self.state = GameState.END
                    self.current_world = "end"
                    self.player_x = SCREEN_WIDTH // 2
                    self.player_y = float(self.ground_y)
                    self.player_vy = 0.0
                    self.on_ground = True
                    self._init_end_crystals()

    def handle_end_events(self, event):
        """Handle events in End"""
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_q:
                if not self.in_question:

                    crystal_id = self._get_nearby_crystal()
                    if crystal_id is not None and crystal_id not in self.end_crystal_answered:
                        self._current_crystal_id = crystal_id
                        self.difficulty_level = Difficulty.MEDIUM
                        self.load_next_question()
                        self.in_question = True

            elif event.key == pygame.K_1 and self.bread_count > 0:
                self.bread_count -= 1
                self.health = min(self.max_health, self.health + 1)
                play_sound("heal")

            elif event.key == pygame.K_2 and self.golden_apple_count > 0:
                self.golden_apple_count -= 1
                self.health = min(self.max_health, self.health + 3)
                play_sound("heal")

            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if not self.in_question and self.on_ground:
                    play_sound("jump")
                    self.player_vy = self.jump_vy
                    self.on_ground = False

    def _switch_overworld_map(self, enter_from):
        self.map_seed = random.randint(0, 10000)
        self.map_changes += 1

        if random.random() < 0.4:
            available = [b for b in self.biomes if b != self.current_biome]
            if available:
                self.current_biome = random.choice(available)

        self.overworld_items = []
        self.overworld_tree_hits = set()
        self.overworld_cactus_hits = set()
        self._fall_peak_y = None
        self._biome_enter_time = pygame.time.get_ticks()
        self._badlands_last_damage_time = 0

        if self.current_biome == "alpine":
            self._generate_alpine_platforms()

        item_type = None
        if self.current_biome not in ('ocean', 'alpine'):
            r = random.random()
            if r < 0.5:
                item_type = "bread"
            elif r < 0.8:
                item_type = "golden_apple"
            elif r < 0.9:
                item_type = "totem"

        if item_type:
            ground_y = SCREEN_HEIGHT - 200
            item_x = random.randint(100, SCREEN_WIDTH - 100)
            item_y = ground_y - 30
            current_time = pygame.time.get_ticks()
            self.overworld_items.append({
                "type": item_type,
                "x": item_x,
                "y": item_y,
                "spawn_time": current_time
            })

        if enter_from == "right":
            self.player_x = 60
        else:
            self.player_x = 60

        if self.current_biome == "alpine" and self.alpine_platforms:
            px, py, pw, ph = self.alpine_platforms[0]
            self.player_x = px + pw // 2 - 10
            self.player_y = float(py)
        else:
            self.player_y = float(self.ground_y)

        self.player_vy = 0.0
        self.on_ground = True

        self._last_map_check_x = self.player_x

    def _spawn_overworld_item(self):
        if self.current_world != "overworld" or self.in_question:
            return None

        if self.current_biome in ('ocean', 'alpine'):
            return None

        rand = random.random()
        item_type = None

        if rand < 0.01:
            item_type = "totem"
        elif rand < 0.11:
            item_type = "golden_apple"
        elif rand < 0.41:
            item_type = "bread"

        if item_type:
            ground_y = SCREEN_HEIGHT - 200
            item_x = random.randint(100, SCREEN_WIDTH - 100)
            item_y = ground_y - 30

            current_time = pygame.time.get_ticks()
            self.overworld_items.append({
                "type": item_type,
                "x": item_x,
                "y": item_y,
                "spawn_time": current_time
            })

    def _check_item_collection(self):
        if self.current_world != "overworld":
            return None

        ground_y = SCREEN_HEIGHT - 200
        player_y = self.player_y
        collection_distance = 40
        current_time = pygame.time.get_ticks()

        items_to_remove = []
        for item in self.overworld_items:

            distance = ((self.player_x - item["x"]) ** 2 + (player_y - item["y"]) ** 2) ** 0.5
            if distance < collection_distance:

                play_sound("collect")
                if item["type"] == "bread":
                    self.bread_count += 1
                elif item["type"] == "golden_apple":
                    self.golden_apple_count += 1
                elif item["type"] == "totem":
                    self.totem_count += 1
                items_to_remove.append(item)

        for item in items_to_remove:
            if item in self.overworld_items:
                self.overworld_items.remove(item)

    def _check_overworld_tree_hazards(self):
        if self.current_world != "overworld":
            return None

        player_rect = pygame.Rect(
            self.player_x - 20,
            int(self.player_y) - 80,
            40,
            80
        )

        ground_y = SCREEN_HEIGHT - 200
        block_size = 40
        rng = random.Random(self.map_seed)

        if self.current_biome == "forest":
            tree_positions = []
            for _ in range(6):
                tree_x = rng.randint(120, SCREEN_WIDTH - 120)
                if any(abs(tree_x - tx) < 80 for tx in tree_positions):
                    continue
                tree_positions.append(tree_x)

            tree_y = ground_y - 80
            for idx, tree_x in enumerate(tree_positions):
                if idx in self.overworld_tree_hits:
                    continue
                trunk_rect = pygame.Rect(tree_x, tree_y, block_size, 80)
                if player_rect.colliderect(trunk_rect):
                    play_sound("hurt")
                    self.health = max(0, self.health - 1)
                    self._hurt_flash_until = pygame.time.get_ticks() + 300
                    self.overworld_tree_hits.add(idx)
                    if self.health <= 0:
                        self._try_totem_or_death()
                    return None

        elif self.current_biome == "desert":
            cactus_positions = []
            for _ in range(4):
                cx = rng.randint(80, SCREEN_WIDTH - 80)
                if any(abs(cx - ec) < 60 for ec in cactus_positions):
                    continue
                cactus_positions.append(cx)

            for idx, cx in enumerate(cactus_positions):
                if idx in self.overworld_cactus_hits:
                    continue
                cactus_rect = pygame.Rect(cx, ground_y - 60, 30, 60)
                if player_rect.colliderect(cactus_rect):
                    play_sound("hurt")
                    self.health = max(0, self.health - 1)
                    self._hurt_flash_until = pygame.time.get_ticks() + 300
                    self.overworld_cactus_hits.add(idx)
                    if self.health <= 0:
                        self._try_totem_or_death()
                    return None

    def _generate_alpine_platforms(self):
        ground_y = SCREEN_HEIGHT - 200
        rng = random.Random(self.map_seed)
        platforms = []

        platforms.append((40, ground_y - 40, 130, 25))

        x = 220
        last_y = ground_y - 40
        while x < SCREEN_WIDTH - 200:
            h_diff = rng.randint(-100, 100)
            next_y = max(ground_y - 250, min(ground_y - 50, last_y + h_diff))
            w = rng.randint(80, 140)
            gap = rng.randint(90, 150)
            x += gap
            if x + w > SCREEN_WIDTH - 100:
                break
            platforms.append((x, next_y, w, 25))
            last_y = next_y
            x += w

        platforms.append((SCREEN_WIDTH - 160, ground_y - 80, 150, 25))
        self.alpine_platforms = platforms

    def _get_alpine_landing_platform(self):
        for px, py, pw, ph in self.alpine_platforms:
            if px <= self.player_x <= px + pw:
                if self.player_vy >= 0 and self.player_y >= py - 15 and self.player_y <= py + ph + 50:
                    fall_dist = py - self._fall_peak_y if self._fall_peak_y is not None else 0
                    return (py, max(0, fall_dist))
        return (None, 0)

    def _check_alpine_on_platform(self):
        for px, py, pw, ph in self.alpine_platforms:
            if px <= self.player_x <= px + pw:
                if abs(self.player_y - py) < 5:
                    return True
        return False

    def _check_badlands_timer(self):
        if self.current_world != "overworld" or self.current_biome != "badlands":
            return None

        now = pygame.time.get_ticks()
        elapsed_sec = (now - self._biome_enter_time) / 1000
        if elapsed_sec <= 3:
            return None

        over_sec = int(elapsed_sec - 3)
        if over_sec > 0 and now - self._badlands_last_damage_time >= 1000:
            self._badlands_last_damage_time = now
            self.health = max(0, self.health - 1)
            play_sound("hurt")
            self._hurt_flash_until = now + 300
            if self.health <= 0:
                self._try_totem_or_death()

    def _check_map_change(self):
        if not hasattr(self, "_last_map_check_x"):
            self._last_map_check_x = self.player_x

        if abs(self.player_x - self._last_map_check_x) > 100:
            self._last_map_check_x = self.player_x
            self.map_changes += 1

    def _init_end_crystals(self):
        self.end_crystal_questions = list(range(self.end_crystal_count))
        self.end_crystal_answered = []
        self.end_crystal_failed = []
        self._current_crystal_id = None
        self._last_map_check_x = getattr(self, "player_x", SCREEN_WIDTH // 2)

    def _get_nearby_crystal(self):
        crystal_positions = [200, 400, 600, 800, 1000]
        for i, pos in enumerate(crystal_positions):
            if abs(self.player_x - pos) < 50:
                return i
        return None

    def _try_totem_or_death(self):
        if self.current_world == "overworld" and self.totem_count > 0:
            self.totem_count -= 1
            self.health = 5
            play_sound("totem")
            if self.current_biome == "alpine" and self.alpine_platforms:
                px, py, pw, ph = self.alpine_platforms[0]
                self.player_x = px + pw // 2 - 10
                self.player_y = float(py)
                self.player_vy = 0.0
                self.on_ground = True
                self._fall_peak_y = None
            else:
                self.player_y = float(self.ground_y)
                self.player_vy = 0.0
                self.on_ground = True
            return None
        self._handle_death()

    def _handle_death(self):
        play_sound("death")
        self.obsidian_count = 0
        self.ender_pearl_count = 0
        self.blaze_rod_count = 0
        self.bread_count = 0
        self.golden_apple_count = 0
        self.totem_count = 0
        self.score = 0
        self.questions_answered = 0
        self.streak = 0
        self.health = 10
        self.current_world = "overworld"
        self.current_biome = "forest"
        self._fall_peak_y = None
        self._biome_enter_time = pygame.time.get_ticks()
        self._badlands_last_damage_time = 0
        self._hurt_flash_until = 0
        self.overworld_items = []
        self.state = GameState.OVERWORLD
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = float(self.ground_y)
        self.player_vy = 0.0
        self.on_ground = True
        self.overworld_tree_hits = set()
        self.overworld_cactus_hits = set()
        self.map_seed = random.randint(0, 10000)
        self.map_changes = 0
        self.piglin_fortress_questions = 0
        self.nether_fortress_questions = 0
        self.end_crystal_answered = []
        self.end_crystal_failed = []
        self._last_map_check_x = self.player_x

    def update(self):
        """Update game state"""
        if self.state == GameState.QUESTION:

            if self.question_start_time > 0:
                self.question_elapsed_time = (pygame.time.get_ticks() - self.question_start_time) / 1000

        elif self.state == GameState.OVERWORLD:

            if not self.in_question:
                self._check_item_collection()
                self._check_overworld_tree_hazards()
                self._check_badlands_timer()

            if self.in_question:
                return

            keys = pygame.key.get_pressed()
            old_x = self.player_x

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_x = self.player_x - self.player_speed
                self.player_x = max(50, new_x)

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_x = self.player_x + self.player_speed
                if new_x >= SCREEN_WIDTH - 50:
                    self._switch_overworld_map("right")
                else:
                    self.player_x = new_x

            if abs(old_x - self.player_x) > 0:
                self._check_map_change()

            ground_y = SCREEN_HEIGHT - 200
            if self.current_biome == "alpine":
                if self.on_ground:
                    if not self._check_alpine_on_platform():
                        self.on_ground = False

                if not self.on_ground:
                    if self._fall_peak_y is None:
                        self._fall_peak_y = self.player_y
                    else:
                        self._fall_peak_y = min(self._fall_peak_y, self.player_y)

                    self.player_vy += self.gravity
                    self.player_y += self.player_vy

                    plat_y, _ = self._get_alpine_landing_platform()
                    if plat_y is not None:
                        self.player_y = float(plat_y)
                        self.player_vy = 0.0
                        self.on_ground = True
                        self._fall_peak_y = None
                    elif self.player_y >= ground_y:
                        self._try_totem_or_death()
                        self._fall_peak_y = None
            else:
                if not self.on_ground:
                    if self._fall_peak_y is None:
                        self._fall_peak_y = self.player_y
                    else:
                        self._fall_peak_y = min(self._fall_peak_y, self.player_y)

                    self.player_vy += self.gravity
                    self.player_y += self.player_vy

                if self.player_y >= ground_y:
                    self._fall_peak_y = None
                    self.player_y = float(ground_y)
                    self.player_vy = 0.0
                    self.on_ground = True

                if self.on_ground and self.player_y > ground_y:
                    self.player_y = float(ground_y)

        elif self.state == GameState.NETHER:

            if self.in_question:
                return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player_x = max(50, self.player_x - self.player_speed)

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player_x = min(SCREEN_WIDTH - 50, self.player_x + self.player_speed)

            if not self.on_ground:
                self.player_vy += self.gravity
                self.player_y += self.player_vy

            if self.player_y >= self.ground_y:
                self.player_y = float(self.ground_y)
                self.player_vy = 0.0
                self.on_ground = True

            if self.on_ground and self.player_y > self.ground_y:
                self.player_y = float(self.ground_y)

        elif self.state == GameState.END:

            if self.in_question:
                return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player_x = max(50, self.player_x - self.player_speed)

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player_x = min(SCREEN_WIDTH - 50, self.player_x + self.player_speed)

            if not self.on_ground:
                self.player_vy += self.gravity
                self.player_y += self.player_vy

            if self.player_y >= self.ground_y:
                self.player_y = float(self.ground_y)
                self.player_vy = 0.0
                self.on_ground = True

            if self.on_ground and self.player_y > self.ground_y:
                self.player_y = float(self.ground_y)

        elif self.state == GameState.FEEDBACK:
            if self.is_answer_correct and pygame.time.get_ticks() - self.feedback_timer > 2000:
                self.in_question = False

                if self.health <= 0:
                    self._handle_death()
                    return

                if self.current_world == "overworld":
                    self.state = GameState.OVERWORLD
                elif self.current_world == "nether":
                    self.state = GameState.NETHER
                elif self.current_world == "end":
                    self.state = GameState.END

                    if isinstance(self.end_crystal_answered, list) and len(self.end_crystal_answered) >= self.end_crystal_count:
                        self.state = GameState.RESULTS

    def draw_menu(self):
        self.screen.fill(MC_SKY)
        self._start_lobby_music()
        ground_y = SCREEN_HEIGHT - 180
        block_size = 40

        for y in range(0, SCREEN_HEIGHT, 3):
            t = y / SCREEN_HEIGHT
            r = int(113 * (1 - t) + 30 * t)
            g = int(197 * (1 - t) + 100 * t)
            b = int(207 * (1 - t) + 180 * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        for cx, cy, w, h in ((200, 120, 120, 40), (600, 80, 150, 35), (950, 150, 100, 30)):
            pygame.draw.ellipse(self.screen, (255, 255, 255), (cx, cy, w, h))
            pygame.draw.ellipse(self.screen, (240, 248, 255), (cx + 20, cy + 5, w - 40, h - 10))

        for x in range(0, SCREEN_WIDTH, block_size):
            grass_rect = pygame.Rect(x, ground_y, block_size, block_size)
            pygame.draw.rect(self.screen, MC_GRASS, grass_rect)
            pygame.draw.rect(self.screen, (80, 140, 60), grass_rect, 2)

        for x in range(0, SCREEN_WIDTH, block_size):
            dirt_rect = pygame.Rect(x, ground_y + block_size, block_size, block_size * 2)
            pygame.draw.rect(self.screen, MC_DIRT, dirt_rect)
            pygame.draw.rect(self.screen, (90, 70, 50), dirt_rect, 1)

        sign_w, sign_h = (520, 140)
        sign_x = (SCREEN_WIDTH - sign_w) // 2
        sign_y = 60
        pygame.draw.rect(self.screen, (139, 90, 43), (sign_x, sign_y, sign_w, sign_h))
        pygame.draw.rect(self.screen, (100, 65, 30), (sign_x, sign_y, sign_w, sign_h), 4)
        pygame.draw.rect(self.screen, (180, 140, 90), (sign_x + 4, sign_y + 4, sign_w - 8, sign_h - 8), 2)
        title = self.font_large.render("Minecraft Quiz", True, (50, 40, 20))
        title2 = self.font_large.render("and Adventure", True, (50, 40, 20))
        self.screen.blit(title, (sign_x + (sign_w - title.get_width()) // 2, sign_y + 25))
        self.screen.blit(title2, (sign_x + (sign_w - title2.get_width()) // 2, sign_y + 75))
        subtitle = self.font_small.render("Learn Science Through Play!", True, (80, 70, 50))
        self.screen.blit(subtitle, (sign_x + (sign_w - subtitle.get_width()) // 2, sign_y + 115))

        button_rect = pygame.Rect(400, 230, 400, 70)
        pygame.draw.rect(self.screen, (80, 180, 80), button_rect)
        pygame.draw.rect(self.screen, (50, 120, 50), button_rect, 3)
        start_text = self.font_medium.render("Start Random Game", True, WHITE)
        start_rect = start_text.get_rect(center=button_rect.center)
        self.screen.blit(start_text, start_rect)

        leaderboard_rect = pygame.Rect(400, 315, 400, 55)
        pygame.draw.rect(self.screen, (120, 80, 160), leaderboard_rect)
        pygame.draw.rect(self.screen, (80, 50, 110), leaderboard_rect, 3)
        leaderboard_text = self.font_small.render("View Leaderboard", True, WHITE)
        leaderboard_text_rect = leaderboard_text.get_rect(center=leaderboard_rect.center)
        self.screen.blit(leaderboard_text, leaderboard_text_rect)

        topic_title = self.font_small.render("Or choose a topic:", True, (40, 35, 30))
        self.screen.blit(topic_title, (400, 390))

        topic_names = {
            'water_cycle': "Water Cycle",
            'states_of_matter': "States of Matter",
            'solar_system': "Solar System",
            'plants': "Plants",
            'animals': "Animals",
        }

        for i, topic in enumerate(self.topics):
            y_pos = 420 + i * 58
            topic_rect = pygame.Rect(400, y_pos, 400, 48)
            color = (150, 110, 190) if topic == self.current_topic else (90, 130, 180)
            pygame.draw.rect(self.screen, color, topic_rect)
            pygame.draw.rect(self.screen, (50, 50, 80), topic_rect, 2)
            topic_text = self.font_small.render(topic_names.get(topic, topic), True, WHITE)
            text_rect = topic_text.get_rect(center=topic_rect.center)
            self.screen.blit(topic_text, text_rect)

        hint = self.font_tiny.render("~ \u7248 P \u7248\u6743\u58f0\u660e | \u5feb\u6377: Ctrl+8=\u5c71\u8109 Ctrl+9=\u6d77\u6d0b Ctrl+0=\u8352\u5730", True, (60, 60, 80))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 35))

    def draw_steve(self, x, y, hurt_flash):
        head_size = 20
        body_width = 16
        body_height = 24
        leg_width = 8
        leg_height = 20
        arm_width = 8
        arm_height = 20

        y_base = y - leg_height - body_height // 2
        skin = (255, 100, 100) if hurt_flash else MC_STEVE_SKIN
        shirt = (255, 80, 80) if hurt_flash else MC_STEVE_SHIRT
        pants = (180, 50, 50) if hurt_flash else MC_STEVE_PANTS

        head_rect = pygame.Rect(x - head_size // 2, y_base - head_size - body_height // 2, head_size, head_size)
        pygame.draw.rect(self.screen, skin, head_rect)
        pygame.draw.rect(self.screen, BLACK, head_rect, 2)

        eye_size = 3
        left_eye = (x - 5, y_base - head_size - body_height // 2 + 6)
        right_eye = (x + 2, y_base - head_size - body_height // 2 + 6)
        pygame.draw.rect(self.screen, BLACK, (left_eye[0], left_eye[1], eye_size, eye_size))
        pygame.draw.rect(self.screen, BLACK, (right_eye[0], right_eye[1], eye_size, eye_size))

        body_rect = pygame.Rect(x - body_width // 2, y_base - body_height // 2, body_width, body_height)
        pygame.draw.rect(self.screen, shirt, body_rect)
        pygame.draw.rect(self.screen, BLACK, body_rect, 2)

        left_arm_rect = pygame.Rect(x - body_width // 2 - arm_width, y_base - body_height // 2, arm_width, arm_height)
        pygame.draw.rect(self.screen, skin, left_arm_rect)
        pygame.draw.rect(self.screen, BLACK, left_arm_rect, 2)

        right_arm_rect = pygame.Rect(x + body_width // 2, y_base - body_height // 2, arm_width, arm_height)
        pygame.draw.rect(self.screen, skin, right_arm_rect)
        pygame.draw.rect(self.screen, BLACK, right_arm_rect, 2)

        left_leg_rect = pygame.Rect(x - body_width // 4 - leg_width // 2, y_base + body_height // 2, leg_width, leg_height)
        pygame.draw.rect(self.screen, pants, left_leg_rect)
        pygame.draw.rect(self.screen, BLACK, left_leg_rect, 2)

        right_leg_rect = pygame.Rect(x + body_width // 4 - leg_width // 2, y_base + body_height // 2, leg_width, leg_height)
        pygame.draw.rect(self.screen, pants, right_leg_rect)
        pygame.draw.rect(self.screen, BLACK, right_leg_rect, 2)

    def _draw_item_icon(self, item_type, x, y):
        icon_size = 30

        if item_type == "bread":
            bread_color = (139, 90, 43)
            bread_rect = pygame.Rect(x - icon_size // 2, y - icon_size // 2, icon_size, icon_size)
            pygame.draw.rect(self.screen, bread_color, bread_rect)
            pygame.draw.rect(self.screen, BLACK, bread_rect, 2)
            pygame.draw.line(self.screen, (100, 60, 20),
                             (x - icon_size // 2 + 5, y),
                             (x + icon_size // 2 - 5, y), 2)
            pygame.draw.line(self.screen, (100, 60, 20),
                             (x - icon_size // 2 + 5, y - 5),
                             (x + icon_size // 2 - 5, y - 5), 2)

        elif item_type == "golden_apple":
            apple_color = (255, 215, 0)
            pygame.draw.circle(self.screen, apple_color, (x, y), icon_size // 2)
            pygame.draw.circle(self.screen, BLACK, (x, y), icon_size // 2, 2)
            leaf_color = (34, 139, 34)
            pygame.draw.ellipse(self.screen, leaf_color, (x - 5, y - icon_size // 2 - 5, 10, 8))

        elif item_type == "totem":
            totem_rect = pygame.Rect(x - icon_size // 2, y - icon_size, icon_size, icon_size * 2)
            pygame.draw.rect(self.screen, (255, 215, 0), (x - icon_size // 2, y - icon_size, icon_size, icon_size))
            pygame.draw.rect(self.screen, (139, 90, 43), (x - icon_size // 2, y, icon_size, icon_size))
            pygame.draw.rect(self.screen, BLACK, totem_rect, 2)
            pygame.draw.circle(self.screen, BLACK, (x - 5, y - icon_size // 2), 3)
            pygame.draw.circle(self.screen, BLACK, (x + 5, y - icon_size // 2), 3)

    def _draw_piglin_fortress(self, x, y):
        fortress_width = 200
        fortress_height = 150
        main_rect = pygame.Rect(x, y, fortress_width, fortress_height)

        gold_color = (255, 215, 0)
        pygame.draw.rect(self.screen, gold_color, main_rect)
        pygame.draw.rect(self.screen, BLACK, main_rect, 3)

        top_points = [
            (x, y),
            (x + fortress_width // 2, y - 30),
            (x + fortress_width, y),
        ]
        pygame.draw.polygon(self.screen, (200, 180, 0), top_points)
        pygame.draw.polygon(self.screen, BLACK, top_points, 3)

        door_width = 40
        door_height = 60
        door_x = x + fortress_width // 2 - door_width // 2
        door_y = y + fortress_height - door_height
        door_rect = pygame.Rect(door_x, door_y, door_width, door_height)
        pygame.draw.rect(self.screen, BLACK, door_rect)

        window_size = 15
        window_y = y + 30

        left_window = pygame.Rect(x + 30, window_y, window_size, window_size)
        pygame.draw.rect(self.screen, (100, 50, 0), left_window)
        pygame.draw.rect(self.screen, BLACK, left_window, 2)

        right_window = pygame.Rect(x + fortress_width - 45, window_y, window_size, window_size)
        pygame.draw.rect(self.screen, (100, 50, 0), right_window)
        pygame.draw.rect(self.screen, BLACK, right_window, 2)

        piglin_head_x = x + fortress_width // 2
        piglin_head_y = y - 50

        pygame.draw.circle(self.screen, (255, 200, 150), (piglin_head_x, piglin_head_y), 20)
        pygame.draw.circle(self.screen, BLACK, (piglin_head_x, piglin_head_y), 20, 2)
        pygame.draw.circle(self.screen, BLACK, (piglin_head_x - 8, piglin_head_y - 5), 3)
        pygame.draw.circle(self.screen, BLACK, (piglin_head_x + 8, piglin_head_y - 5), 3)
        pygame.draw.circle(self.screen, (255, 150, 150), (piglin_head_x, piglin_head_y + 5), 5)

    def _draw_nether_fortress(self, x, y):
        fortress_width = 200
        fortress_height = 200
        main_rect = pygame.Rect(x, y, fortress_width, fortress_height)

        fortress_color = (80, 10, 10)
        pygame.draw.rect(self.screen, fortress_color, main_rect)
        pygame.draw.rect(self.screen, BLACK, main_rect, 3)

        tower_width = 40
        tower_height = 250

        left_tower = pygame.Rect(x + 20, y - 50, tower_width, tower_height)
        pygame.draw.rect(self.screen, (60, 5, 5), left_tower)
        pygame.draw.rect(self.screen, BLACK, left_tower, 3)

        right_tower = pygame.Rect(x + fortress_width - 60, y - 50, tower_width, tower_height)
        pygame.draw.rect(self.screen, (60, 5, 5), right_tower)
        pygame.draw.rect(self.screen, BLACK, right_tower, 3)

        left_tower_top = [
            (x + 20, y - 50),
            (x + 40, y - 80),
            (x + 60, y - 50),
        ]
        pygame.draw.polygon(self.screen, (40, 0, 0), left_tower_top)
        pygame.draw.polygon(self.screen, BLACK, left_tower_top, 3)

        right_tower_top = [
            (x + fortress_width - 60, y - 50),
            (x + fortress_width - 40, y - 80),
            (x + fortress_width - 20, y - 50),
        ]
        pygame.draw.polygon(self.screen, (40, 0, 0), right_tower_top)
        pygame.draw.polygon(self.screen, BLACK, right_tower_top, 3)

        door_width = 50
        door_height = 80
        door_x = x + fortress_width // 2 - door_width // 2
        door_y = y + fortress_height - door_height
        door_rect = pygame.Rect(door_x, door_y, door_width, door_height)
        pygame.draw.rect(self.screen, (20, 0, 0), door_rect)
        pygame.draw.rect(self.screen, BLACK, door_rect, 2)

        window_size = 12
        window_y = y + 40

        left_window = pygame.Rect(x + 30, window_y, window_size, window_size)
        pygame.draw.rect(self.screen, (255, 50, 50), left_window)
        pygame.draw.rect(self.screen, BLACK, left_window, 2)

        right_window = pygame.Rect(x + fortress_width - 42, window_y, window_size, window_size)
        pygame.draw.rect(self.screen, (255, 50, 50), right_window)
        pygame.draw.rect(self.screen, BLACK, right_window, 2)

        center_window = pygame.Rect(x + fortress_width // 2 - window_size // 2, window_y, window_size, window_size)
        pygame.draw.rect(self.screen, (255, 50, 50), center_window)
        pygame.draw.rect(self.screen, BLACK, center_window, 2)

        blaze_icon_x = x + fortress_width // 2
        blaze_icon_y = y - 100

        blaze_rect = pygame.Rect(blaze_icon_x - 5, blaze_icon_y - 20, 10, 40)
        pygame.draw.rect(self.screen, ORANGE, blaze_rect)
        pygame.draw.rect(self.screen, BLACK, blaze_rect, 2)

        for i in range(3):
            flame_y = blaze_icon_y - 20 - i * 5
            flame_points = [
                (blaze_icon_x - 8, flame_y),
                (blaze_icon_x, flame_y - 5),
                (blaze_icon_x + 8, flame_y),
            ]
            pygame.draw.polygon(self.screen, (255, 150, 0), flame_points)

    def draw_overworld(self):
        rng = random.Random(self.map_seed)

        if self.current_biome == "desert":
            self.screen.fill((255, 230, 180))
        elif self.current_biome == "snow":
            self.screen.fill((200, 220, 255))
        elif self.current_biome == "alpine":
            self.screen.fill((180, 195, 210))
        elif self.current_biome == "ocean":
            self.screen.fill((135, 180, 220))
        elif self.current_biome == "badlands":
            self.screen.fill((220, 180, 140))
        else:
            self.screen.fill(MC_SKY)

        ground_y = SCREEN_HEIGHT - 200
        block_size = 40

        if self.current_biome == "desert":
            for x in range(0, SCREEN_WIDTH, block_size):
                sand_rect = pygame.Rect(x, ground_y, block_size, block_size)
                pygame.draw.rect(self.screen, SAND, sand_rect)
                pygame.draw.rect(self.screen, BLACK, sand_rect, 2)
                for layer in range(1, 4):
                    dark_rect = pygame.Rect(x, ground_y + layer * block_size, block_size, block_size)
                    pygame.draw.rect(self.screen, SAND_DARK, dark_rect)
                    pygame.draw.rect(self.screen, BLACK, dark_rect, 2)

            cactus_positions = []
            for _ in range(4):
                cx = rng.randint(80, SCREEN_WIDTH - 80)
                if any(abs(cx - c) < 80 for c in cactus_positions):
                    continue
                cactus_positions.append(cx)
                base = pygame.Rect(cx, ground_y - 60, 30, 60)
                pygame.draw.rect(self.screen, (34, 139, 34), base)
                pygame.draw.rect(self.screen, BLACK, base, 2)

        elif self.current_biome == "snow":
            for x in range(0, SCREEN_WIDTH, block_size):
                snow_rect = pygame.Rect(x, ground_y, block_size, block_size)
                pygame.draw.rect(self.screen, SNOW, snow_rect)
                pygame.draw.rect(self.screen, BLACK, snow_rect, 2)
                for layer in range(1, 4):
                    sd_rect = pygame.Rect(x, ground_y + layer * block_size, block_size, block_size)
                    pygame.draw.rect(self.screen, SNOW_DIRT, sd_rect)
                    pygame.draw.rect(self.screen, BLACK, sd_rect, 2)

            snow_positions = []
            for _ in range(7):
                cx = rng.randint(80, SCREEN_WIDTH - 80)
                if any(abs(cx - c) < 80 for c in snow_positions):
                    continue
                snow_positions.append(cx)
                width = rng.randint(40, 70)
                heap = pygame.Rect(cx, ground_y - 20, width, 20)
                pygame.draw.ellipse(self.screen, WHITE, heap)

        elif self.current_biome == "alpine":
            for i in range(5):
                mx = rng.randint(0, SCREEN_WIDTH)
                mh = rng.randint(80, 180)
                points = [
                    (mx - 60, ground_y + 50),
                    (mx, ground_y - mh),
                    (mx + 60, ground_y + 50),
                ]
                pygame.draw.polygon(self.screen, (160, 170, 185), points)
                pygame.draw.polygon(self.screen, BLACK, points, 1)

            for px, py, pw, ph in self.alpine_platforms:
                plat_rect = pygame.Rect(px, py, pw, ph)
                pygame.draw.rect(self.screen, ALPINE_STONE, plat_rect)
                pygame.draw.rect(self.screen, BLACK, plat_rect, 2)
                snow_rect = pygame.Rect(px, py, pw, 8)
                pygame.draw.rect(self.screen, ALPINE_SNOW, snow_rect)
                pygame.draw.rect(self.screen, BLACK, snow_rect, 1)

        elif self.current_biome == "ocean":
            for x in range(0, SCREEN_WIDTH, block_size):
                water_rect = pygame.Rect(x, ground_y, block_size, block_size)
                pygame.draw.rect(self.screen, OCEAN_BLUE, water_rect)
                pygame.draw.rect(self.screen, BLACK, water_rect, 2)
                for layer in range(1, 4):
                    deep_rect = pygame.Rect(x, ground_y + layer * block_size, block_size, block_size)
                    pygame.draw.rect(self.screen, OCEAN_DEEP, deep_rect)
                    pygame.draw.rect(self.screen, BLACK, deep_rect, 2)

            for wy in range(ground_y - 25, ground_y - 5, 5):
                for wx in range(0, SCREEN_WIDTH, 20):
                    pygame.draw.line(self.screen, (60, 130, 200), (wx, wy), (wx + 10, wy - 3), 2)

        elif self.current_biome == "badlands":
            for x in range(0, SCREEN_WIDTH, block_size):
                terra_rect = pygame.Rect(x, ground_y, block_size, block_size)
                pygame.draw.rect(self.screen, BADLANDS_TERRACOTTA, terra_rect)
                pygame.draw.rect(self.screen, BLACK, terra_rect, 2)
                for layer in range(1, 4):
                    deep_rect = pygame.Rect(x, ground_y + layer * block_size, block_size, block_size)
                    pygame.draw.rect(self.screen, BADLANDS_ORANGE, deep_rect)
                    pygame.draw.rect(self.screen, BLACK, deep_rect, 2)

            for _ in range(4):
                bx = rng.randint(100, SCREEN_WIDTH - 100)
                spike_h = rng.randint(30, 60)
                spike_rect = pygame.Rect(bx, ground_y - spike_h, 25, spike_h)
                pygame.draw.rect(self.screen, SAND_DARK, spike_rect)
                pygame.draw.rect(self.screen, BLACK, spike_rect, 2)

        elif self.current_biome == "plains":
            for x in range(0, SCREEN_WIDTH, block_size):
                grass_rect = pygame.Rect(x, ground_y, block_size, block_size)
                pygame.draw.rect(self.screen, MC_GRASS, grass_rect)
                pygame.draw.rect(self.screen, BLACK, grass_rect, 2)
                for layer in range(1, 4):
                    dirt_rect = pygame.Rect(x, ground_y + layer * block_size, block_size, block_size)
                    pygame.draw.rect(self.screen, MC_DIRT, dirt_rect)
                    pygame.draw.rect(self.screen, BLACK, dirt_rect, 2)

            bush_positions = []
            for _ in range(8):
                cx = rng.randint(80, SCREEN_WIDTH - 80)
                if any(abs(cx - c) < 80 for c in bush_positions):
                    continue
                bush_positions.append(cx)
                bush = pygame.Rect(cx, ground_y - 25, 30, 25)
                pygame.draw.rect(self.screen, MC_GRASS, bush)
                pygame.draw.rect(self.screen, BLACK, bush, 2)

        else:
            for x in range(0, SCREEN_WIDTH, block_size):
                grass_rect = pygame.Rect(x, ground_y, block_size, block_size)
                pygame.draw.rect(self.screen, MC_GRASS, grass_rect)
                pygame.draw.rect(self.screen, BLACK, grass_rect, 2)
                for layer in range(1, 4):
                    dirt_rect = pygame.Rect(x, ground_y + layer * block_size, block_size, block_size)
                    pygame.draw.rect(self.screen, MC_DIRT, dirt_rect)
                    pygame.draw.rect(self.screen, BLACK, dirt_rect, 2)

            tree_positions = []
            for _ in range(6):
                tree_x = rng.randint(120, SCREEN_WIDTH - 120)
                if any(abs(tree_x - t) < 120 for t in tree_positions):
                    continue
                tree_positions.append(tree_x)
                tree_y = ground_y - 80
                trunk_rect = pygame.Rect(tree_x, tree_y, block_size, 80)
                pygame.draw.rect(self.screen, MC_WOOD, trunk_rect)
                pygame.draw.rect(self.screen, BLACK, trunk_rect, 2)
                for leaf_x in (tree_x - block_size, tree_x, tree_x + block_size):
                    for leaf_y in (tree_y - block_size, tree_y - 2 * block_size):
                        leaf_rect = pygame.Rect(leaf_x, leaf_y, block_size, block_size)
                        pygame.draw.rect(self.screen, MC_GRASS, leaf_rect)
                        pygame.draw.rect(self.screen, BLACK, leaf_rect, 2)

        for item in self.overworld_items:
            self._draw_item_icon(item["type"], item["x"], item["y"])

        steve_x = self.player_x
        steve_y = int(self.player_y)
        hurt_flash = pygame.time.get_ticks() < getattr(self, "_hurt_flash_until", 0)
        self.draw_steve(steve_x, steve_y, hurt_flash)

        move_hint = self.font_tiny.render("A/D or Left/Right: Move | SPACE/UP: Jump | Q: Answer | Right Click: Enter Nether (5 Obsidian)", True, WHITE)
        move_bg = pygame.Surface((500, 30))
        move_bg.set_alpha(150)
        move_bg.fill(BLACK)
        self.screen.blit(move_bg, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 100))
        self.screen.blit(move_hint, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT - 95))

        if self.current_biome == "alpine":
            biome_hint = self.font_tiny.render("Alpine Parkour: Jump between platforms! Fall = death (Totem can save you).", True, (255, 200, 200))
            self.screen.blit(biome_hint, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 135))
        elif self.current_biome == "ocean":
            biome_hint = self.font_tiny.render("Ocean: No items here. Keep moving!", True, (200, 220, 255))
            self.screen.blit(biome_hint, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 135))
        elif self.current_biome == "badlands":
            elapsed = (pygame.time.get_ticks() - self._biome_enter_time) / 1000
            remain = max(0, 3 - elapsed)
            biome_hint = self.font_tiny.render(f"Badlands: Leave in {remain:.1f}s or take 1 heart/sec!", True, (255, 180, 100))
            self.screen.blit(biome_hint, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 135))

        items_y = SCREEN_HEIGHT - 200
        items_text = self.font_tiny.render(f"Items: Bread({self.bread_count}) [1] | Apple({self.golden_apple_count}) [2] | Totem({self.totem_count})", True, WHITE)
        items_bg = pygame.Surface((600, 30))
        items_bg.set_alpha(150)
        items_bg.fill(BLACK)
        self.screen.blit(items_bg, (SCREEN_WIDTH // 2 - 300, items_y))
        self.screen.blit(items_text, (SCREEN_WIDTH // 2 - 290, items_y + 5))

        health_x = 20
        health_y = 20
        health_text = self.font_medium.render(f"Health: {self.health}/{self.max_health}", True, WHITE)
        health_bg = pygame.Surface((250, 50))
        health_bg.set_alpha(200)
        health_bg.fill(BLACK)
        self.screen.blit(health_bg, (health_x - 10, health_y - 10))
        self.screen.blit(health_text, (health_x, health_y))

        bar_width = 200
        bar_height = 20
        bar_x = health_x
        bar_y = health_y + 40
        health_ratio = self.health / self.max_health

        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        health_color = GREEN if health_ratio > 0.5 else (YELLOW if health_ratio > 0.25 else RED)
        pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

        hint_text = self.font_small.render("Press Q to start answering questions", True, WHITE)
        hint_bg = pygame.Surface((400, 40))
        hint_bg.set_alpha(180)
        hint_bg.fill(BLACK)
        hint_rect = hint_bg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint_bg, hint_rect)
        hint_text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint_text, hint_text_rect)

        info_y = 80
        score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
        questions_text = self.font_small.render(f"Questions: {self.questions_answered}/{self.total_questions}", True, WHITE)
        info_bg = pygame.Surface((250, 80))
        info_bg.set_alpha(200)
        info_bg.fill(BLACK)
        self.screen.blit(info_bg, (health_x - 10, info_y - 10))
        self.screen.blit(score_text, (health_x, info_y))
        self.screen.blit(questions_text, (health_x, info_y + 30))

        obsidian_x = SCREEN_WIDTH - 250
        obsidian_y = SCREEN_HEIGHT - 150
        obsidian_text = self.font_medium.render(f"Obsidian: {self.obsidian_count}", True, WHITE)
        obsidian_bg = pygame.Surface((230, 60))
        obsidian_bg.set_alpha(200)
        obsidian_bg.fill((50, 50, 50))
        self.screen.blit(obsidian_bg, (obsidian_x - 10, obsidian_y - 10))
        self.screen.blit(obsidian_text, (obsidian_x, obsidian_y))

        for i in range(min(self.obsidian_count, 10)):
            icon_x = obsidian_x + (i % 5) * 35
            icon_y = obsidian_y + 40 + (i // 5) * 35
            obsidian_icon = pygame.Rect(icon_x, icon_y, 30, 30)
            pygame.draw.rect(self.screen, (20, 20, 30), obsidian_icon)
            pygame.draw.rect(self.screen, WHITE, obsidian_icon, 2)

        if self.world_start_time > 0:
            world_elapsed = (pygame.time.get_ticks() - self.world_start_time) / 1000
            minutes = int(world_elapsed // 60)
            seconds = int(world_elapsed % 60)
            timer_text = self.font_small.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
            timer_bg = pygame.Surface((200, 40))
            timer_bg.set_alpha(200)
            timer_bg.fill(BLACK)
            timer_x = obsidian_x
            timer_y = obsidian_y + 70
            self.screen.blit(timer_bg, (timer_x - 10, timer_y - 10))
            self.screen.blit(timer_text, (timer_x, timer_y))

    def draw_nether(self):
        self.screen.fill(MC_NETHER)

        ground_y = SCREEN_HEIGHT - 200
        block_size = 40
        for x in range(0, SCREEN_WIDTH, block_size):
            netherrack_rect = pygame.Rect(x, ground_y, block_size, block_size)
            pygame.draw.rect(self.screen, MC_NETHERRACK, netherrack_rect)
            pygame.draw.rect(self.screen, BLACK, netherrack_rect, 2)

        for i in range(3):
            lava_x = 100 + i * 350
            lava_rect = pygame.Rect(lava_x, ground_y - 20, 200, 20)
            pygame.draw.rect(self.screen, MC_LAVA, lava_rect)
            pygame.draw.rect(self.screen, ORANGE, lava_rect, 2)
            for j in range(3):
                bubble_x = lava_x + 30 + j * 50
                bubble_y = ground_y - 25
                pygame.draw.circle(self.screen, (255, 150, 0), (bubble_x, bubble_y), 5)

        piglin_fortress_x = 100
        piglin_fortress_y = ground_y - 150
        self._draw_piglin_fortress(piglin_fortress_x, piglin_fortress_y)

        nether_fortress_x = SCREEN_WIDTH - 300
        nether_fortress_y = ground_y - 200
        self._draw_nether_fortress(nether_fortress_x, nether_fortress_y)

        if self.player_x < SCREEN_WIDTH // 2:
            progress_text = self.font_small.render(f"Questions: {self.piglin_fortress_questions}/3", True, YELLOW)
            progress_bg = pygame.Surface((250, 40))
            progress_bg.set_alpha(200)
            progress_bg.fill(BLACK)
            self.screen.blit(progress_bg, (50, 50))
            self.screen.blit(progress_text, (60, 60))
            if self.piglin_fortress_questions < 3:
                hint_text = self.font_tiny.render("Press Q to answer (Hard) | +1 Pearl, -3 Hearts", True, WHITE)
                self.screen.blit(hint_text, (50, 100))
        else:
            progress_text = self.font_small.render(f"Questions: {self.nether_fortress_questions}/3", True, RED)
            progress_bg = pygame.Surface((250, 40))
            progress_bg.set_alpha(200)
            progress_bg.fill(BLACK)
            self.screen.blit(progress_bg, (SCREEN_WIDTH - 300, 50))
            self.screen.blit(progress_text, (SCREEN_WIDTH - 290, 60))
            if self.nether_fortress_questions < 3:
                hint_text = self.font_tiny.render("Press Q to answer (Medium) | +1 Rod, -2 Hearts", True, WHITE)
                self.screen.blit(hint_text, (SCREEN_WIDTH - 300, 100))

        steve_y = int(self.player_y)
        hurt_flash = pygame.time.get_ticks() < getattr(self, "_hurt_flash_until", 0)
        self.draw_steve(self.player_x, steve_y, hurt_flash)

        self._draw_game_ui()

        items_hint = self.font_tiny.render("Items: [1] Bread | [2] Golden Apple", True, WHITE)
        items_hint_bg = pygame.Surface((350, 30))
        items_hint_bg.set_alpha(150)
        items_hint_bg.fill(BLACK)
        self.screen.blit(items_hint_bg, (SCREEN_WIDTH - 360, SCREEN_HEIGHT - 50))
        self.screen.blit(items_hint, (SCREEN_WIDTH - 350, SCREEN_HEIGHT - 45))

        move_hint = self.font_tiny.render("A/D or Left/Right: Move | Left: Piglin Fortress | Right: Nether Fortress", True, WHITE)
        move_bg = pygame.Surface((600, 30))
        move_bg.set_alpha(150)
        move_bg.fill(BLACK)
        self.screen.blit(move_bg, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT - 100))
        self.screen.blit(move_hint, (SCREEN_WIDTH // 2 - 290, SCREEN_HEIGHT - 95))

        items_x = SCREEN_WIDTH - 300
        items_y = 200
        pearl_text = self.font_small.render(f"Ender Pearls: {self.ender_pearl_count}/3", True, PURPLE)
        rod_text = self.font_small.render(f"Blaze Rods: {self.blaze_rod_count}/3", True, ORANGE)
        items_bg = pygame.Surface((280, 80))
        items_bg.set_alpha(200)
        items_bg.fill(BLACK)
        self.screen.blit(items_bg, (items_x - 10, items_y - 10))
        self.screen.blit(pearl_text, (items_x, items_y))
        self.screen.blit(rod_text, (items_x, items_y + 30))

        if self.ender_pearl_count >= 3 and self.blaze_rod_count >= 3:
            end_hint = self.font_small.render("Right Click: Enter End (3 Pearls + 3 Rods)", True, GREEN)
            end_bg = pygame.Surface((400, 40))
            end_bg.set_alpha(200)
            end_bg.fill(BLACK)
            self.screen.blit(end_bg, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 100))
            self.screen.blit(end_hint, (SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT - 95))

    def draw_end(self):
        try:
            self._draw_end_impl()
        except Exception as e:
            self.screen.fill(MC_END_SKY)
            err_text = self.font_small.render(f"End dimension loading... ({type(e).__name__})", True, WHITE)
            self.screen.blit(err_text, (100, 100))
            detail = self.font_tiny.render(str(e), True, (200, 200, 200))
            self.screen.blit(detail, (100, 150))
            print(f"[draw_end] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def _draw_end_impl(self):
        self.screen.fill(MC_END_SKY)
        ground_y = SCREEN_HEIGHT - 200
        block_size = 40

        if not isinstance(self.end_crystal_answered, list):
            self.end_crystal_answered = []
        if not isinstance(self.end_crystal_failed, list):
            self.end_crystal_failed = []

        try:
            _ = int(self.player_y)
        except (ValueError, TypeError):
            self.player_y = float(self.ground_y)

        for y in range(0, SCREEN_HEIGHT, 4):
            t = y / SCREEN_HEIGHT
            r = int(20 * (1 - t) + 10 * t)
            g = int(10 * (1 - t) + 2 * t)
            b = int(30 * (1 - t) + 8 * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        rng = random.Random(42)
        sy_max = max(1, ground_y)
        for _ in range(60):
            sx = rng.randint(0, max(1, SCREEN_WIDTH))
            sy = rng.randint(0, sy_max)
            star_bright = rng.randint(100, 255)
            star_color = (star_bright, star_bright, min(255, star_bright + 20))
            pygame.draw.circle(self.screen, star_color, (sx, sy), 1)

        for x in range(0, SCREEN_WIDTH, block_size):
            end_stone_rect = pygame.Rect(x, ground_y, block_size, block_size)
            pygame.draw.rect(self.screen, MC_END_STONE, end_stone_rect)
            pygame.draw.rect(self.screen, BLACK, end_stone_rect, 2)

        void_rect = pygame.Rect(0, ground_y + block_size, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (5, 2, 15), void_rect)

        crystal_positions = [200, 400, 600, 800, 1000]
        ticks = pygame.time.get_ticks()
        for i, pos in enumerate(crystal_positions):
            if i in self.end_crystal_answered:
                continue

            pulse = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(ticks / 600))
            crystal_height = 150

            glow_rect = pygame.Rect(pos - 25, ground_y - crystal_height - 30, 50, crystal_height + 40)
            glow_surf = pygame.Surface((50, crystal_height + 40))
            alpha_val = max(0, min(255, int(30 * pulse)))
            glow_surf.set_alpha(alpha_val)
            glow_surf.fill((150, 80, 255))
            self.screen.blit(glow_surf, (pos - 25, ground_y - crystal_height - 30))

            crystal_rect = pygame.Rect(pos - 15, ground_y - crystal_height, 30, crystal_height)
            pygame.draw.rect(self.screen, MC_PURPLE, crystal_rect)
            pygame.draw.rect(self.screen, WHITE, crystal_rect, 2)

            crystal_top = pygame.Rect(pos - 20, ground_y - crystal_height - 20, 40, 20)
            pygame.draw.rect(self.screen, YELLOW, crystal_top)
            pygame.draw.rect(self.screen, WHITE, crystal_top, 2)

            highlight = pygame.Rect(pos - 8, ground_y - crystal_height - 16, 16, 8)
            pygame.draw.rect(self.screen, (255, 255, 200), highlight)

            if abs(self.player_x - pos) < 50:
                hint_text = self.font_small.render("Press Q to answer!", True, YELLOW)
                hint_bg = pygame.Surface((280, 40))
                hint_bg.set_alpha(200)
                hint_bg.fill(BLACK)
                self.screen.blit(hint_bg, (pos - 140, ground_y - crystal_height - 60))
                self.screen.blit(hint_text, (pos - 130, ground_y - crystal_height - 55))

        steve_y = int(self.player_y)
        hurt_flash = pygame.time.get_ticks() < getattr(self, "_hurt_flash_until", 0)
        self.draw_steve(self.player_x, steve_y, hurt_flash)

        self._draw_game_ui()

        progress_text = self.font_medium.render(f"Crystals Destroyed: {len(self.end_crystal_answered)}/{self.end_crystal_count}", True, YELLOW)
        progress_bg = pygame.Surface((400, 50))
        progress_bg.set_alpha(200)
        progress_bg.fill(BLACK)
        self.screen.blit(progress_bg, (SCREEN_WIDTH // 2 - 200, 50))
        self.screen.blit(progress_text, (SCREEN_WIDTH // 2 - 190, 60))

        items_hint = self.font_tiny.render("Items: [1] Bread | [2] Golden Apple | Totem (auto on death)", True, WHITE)
        items_bg = pygame.Surface((450, 30))
        items_bg.set_alpha(150)
        items_bg.fill(BLACK)
        self.screen.blit(items_bg, (SCREEN_WIDTH - 470, SCREEN_HEIGHT - 50))
        self.screen.blit(items_hint, (SCREEN_WIDTH - 460, SCREEN_HEIGHT - 45))

    def _draw_game_ui(self):
        health_x = 20
        health_y = 20
        health_text = self.font_medium.render(f"Health: {self.health}/{self.max_health}", True, WHITE)
        health_bg = pygame.Surface((250, 50))
        health_bg.set_alpha(200)
        health_bg.fill(BLACK)
        self.screen.blit(health_bg, (health_x - 10, health_y - 10))
        self.screen.blit(health_text, (health_x, health_y))

        bar_width = 200
        bar_height = 20
        bar_x = health_x
        bar_y = health_y + 40
        health_ratio = max(0, min(1, self.health / max(1, self.max_health)))
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        health_color = GREEN if health_ratio > 0.5 else YELLOW if health_ratio > 0.25 else RED
        health_bar_w = max(0, min(bar_width, int(bar_width * health_ratio)))
        pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, health_bar_w, bar_height))
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

        if getattr(self, "world_start_time", 0) > 0:
            world_elapsed = (pygame.time.get_ticks() - self.world_start_time) / 1000
            minutes = int(world_elapsed // 60)
            seconds = int(world_elapsed % 60)
            timer_text = self.font_small.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
            timer_bg = pygame.Surface((200, 40))
            timer_bg.set_alpha(200)
            timer_bg.fill(BLACK)
            timer_x = SCREEN_WIDTH - 250
            timer_y = SCREEN_HEIGHT - 80
            self.screen.blit(timer_bg, (timer_x - 10, timer_y - 10))
            self.screen.blit(timer_text, (timer_x, timer_y))

    def _get_answer_rect(self, answer_index):
        if not self.current_question:
            return None

        question_y = 200

        image_surface = None
        if self.current_question.image_path:
            image_surface = self._load_image(self.current_question.image_path)

        if image_surface:
            question_y = 150
            image_y = question_y + 50
            img_width, img_height = image_surface.get_size()
            max_width, max_height = (400, 200)
            scale = min(max_width / img_width, max_height / img_height, 1.0)
            if scale < 1.0:
                new_height = int(img_height * scale)
            else:
                new_height = img_height
            answer_y_start = image_y + new_height + 30
        else:
            answer_y_start = 300

        y_pos = answer_y_start + answer_index * 80
        return pygame.Rect(200, y_pos, 800, 60)

    def draw_question(self):
        self.screen.fill(LIGHT_BLUE)
        score_text = self.font_small.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (50, 50))

        streak_text = self.font_small.render(f"Streak: {self.streak}", True, ORANGE)
        self.screen.blit(streak_text, (50, 100))

        difficulty_text = self.font_tiny.render(
            f"Difficulty: {self.difficulty_level.value}", True, DARK_GRAY)

        self.screen.blit(difficulty_text, (50, 150))

        if self.question_start_time > 0:
            elapsed = self.question_elapsed_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            timer_text = self.font_small.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)

            timer_bg = pygame.Surface((200, 40))
            timer_bg.set_alpha(180)
            timer_bg.fill(BLACK)
            self.screen.blit(timer_bg, (10, 10))
            self.screen.blit(timer_text, (15, 15))

        if self.current_question:
            question_text = self.font_medium.render(self.current_question.question, True, BLACK)
            question_y = 200

            image_surface = None
            if self.current_question.image_path:
                image_surface = self._load_image(self.current_question.image_path)

            if image_surface:
                question_y = 150
                question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, question_y))
                self.screen.blit(question_text, question_rect)

                image_y = question_y + 50

                img_width, img_height = image_surface.get_size()
                max_width, max_height = (400, 200)
                scale = min(max_width / img_width, max_height / img_height, 1.0)
                if scale < 1.0:
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    image_surface = pygame.transform.scale(image_surface, (new_width, new_height))

                image_x = (SCREEN_WIDTH - image_surface.get_width()) // 2
                self.screen.blit(image_surface, (image_x, image_y))
                answer_y_start = image_y + image_surface.get_height() + 30
            else:
                question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, question_y))
                self.screen.blit(question_text, question_rect)
                answer_y_start = 300

            mouse_pos = pygame.mouse.get_pos()

            for i, answer in enumerate(self.current_answers):
                y_pos = answer_y_start + i * 80
                answer_rect = pygame.Rect(200, y_pos, 800, 60)

                is_hovered = answer_rect.collidepoint(mouse_pos)

                if is_hovered:
                    button_color = (173, 216, 230)
                    border_color = BLUE
                    border_width = 3
                else:
                    button_color = WHITE
                    border_color = BLACK
                    border_width = 2

                pygame.draw.rect(self.screen, button_color, answer_rect)
                pygame.draw.rect(self.screen, border_color, answer_rect, border_width)

                number_color = BLUE if is_hovered else BLUE
                number_label = self.font_medium.render(f"{i + 1}.", True, number_color)
                number_x = 220
                number_y = y_pos + 15
                self.screen.blit(number_label, (number_x, number_y))

                answer_surface = self.font_small.render(answer, True, BLACK)
                answer_text_x = 280
                answer_text_y = y_pos + 15
                self.screen.blit(answer_surface, (answer_text_x, answer_text_y))

            hint_text = self.font_tiny.render("Press 1, 2, 3, or 4 to select your answer | Press W to exit", True, DARK_GRAY)
            hint_bg = pygame.Surface((600, 30))
            hint_bg.set_alpha(200)
            hint_bg.fill(WHITE)
            self.screen.blit(hint_bg, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT - 50))
            self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 290, SCREEN_HEIGHT - 45))

    def draw_feedback(self):
        self.screen.fill(LIGHT_BLUE)
        if self.current_question:
            question_text = self.font_medium.render(self.current_question.question, True, BLACK)
            question_y = 100
            question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, question_y))
            self.screen.blit(question_text, question_rect)

            image_surface = None
            if self.current_question.image_path:
                image_surface = self._load_image(self.current_question.image_path)

            if image_surface:
                image_y = question_y + 50

                img_width, img_height = image_surface.get_size()
                max_width, max_height = (300, 150)
                scale = min(max_width / img_width, max_height / img_height, 1.0)
                if scale < 1.0:
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    image_surface = pygame.transform.scale(image_surface, (new_width, new_height))

                image_x = (SCREEN_WIDTH - image_surface.get_width()) // 2
                self.screen.blit(image_surface, (image_x, image_y))
                answer_y_start = image_y + image_surface.get_height() + 20
            else:
                answer_y_start = 200

            for i, answer in enumerate(self.current_answers):
                y_pos = answer_y_start + i * 60
                answer_rect = pygame.Rect(200, y_pos, 800, 50)

                if answer == self.current_question.correct_answer:
                    color = GREEN
                elif self.selected_answer == i and answer != self.current_question.correct_answer:
                    color = RED
                else:
                    color = GRAY

                pygame.draw.rect(self.screen, color, answer_rect)
                pygame.draw.rect(self.screen, BLACK, answer_rect, 2)

                answer_surface = self.font_small.render(answer, True, BLACK)
                answer_text_rect = answer_surface.get_rect(center=answer_rect.center)
                self.screen.blit(answer_surface, answer_text_rect)

        lines = self.feedback_message.split("\n")
        y_start = 580
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            if line.startswith("Explanation:"):
                font = self.font_small
                color = DARK_GRAY
            elif line.startswith("Press ESC"):
                font = self.font_small
                color = ORANGE
            else:
                font = self.font_medium
                color = self.feedback_color

            feedback_text = font.render(line, True, color)
            feedback_rect = feedback_text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 50))
            self.screen.blit(feedback_text, feedback_rect)

        score_text = self.font_small.render(f"Total Score: {self.score} | Streak: {self.streak}", True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 200, 700))

    def draw_results(self):
        if not self._score_saved:
            total_time = (pygame.time.get_ticks() - self.world_start_time) / 1000 if self.world_start_time > 0 else 0
            name = (self.player_name or "").strip() or "Player"
            self.leaderboard.add_score(
                name,
                int(max(0, total_time)),
                self.questions_answered,
                "Speedrun"
            )
            self._score_saved = True
            play_sound("complete")

        self.screen.fill(LIGHT_BLUE)

        title = self.font_large.render("Game Complete!", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        name_text = self.font_small.render(f"Player: {self.player_name}", True, DARK_GRAY)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(name_text, name_rect)

        if self.world_start_time > 0:
            total_time = (pygame.time.get_ticks() - self.world_start_time) / 1000
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            time_text = self.font_medium.render(f"Speedrun Time: {minutes:02d}:{seconds:02d}", True, BLACK)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
            self.screen.blit(time_text, time_rect)

        score_text = self.font_small.render(f"Final Score: {self.score}", True, DARK_GRAY)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 340))
        self.screen.blit(score_text, score_rect)

        questions_text = self.font_small.render(
            f"Questions Answered: {self.questions_answered}", True, DARK_GRAY)
        questions_rect = questions_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(questions_text, questions_rect)

        accuracy = self.score / 100 / self.questions_answered if self.questions_answered > 0 else 0
        if accuracy >= 0.8:
            performance = "Excellent work! You're a science superstar! \U0001f31f"
        elif accuracy >= 0.6:
            performance = "Great job! Keep learning and improving! \U0001f4aa"
        else:
            performance = "Good effort! Practice makes perfect! \U0001f4da"

        perf_text = self.font_small.render(performance, True, PURPLE)
        perf_rect = perf_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(perf_text, perf_rect)

        saved_text = self.font_tiny.render("Score saved to leaderboard!", True, GREEN)
        saved_rect = saved_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(saved_text, saved_rect)

        button_rect = pygame.Rect(400, 500, 400, 60)
        pygame.draw.rect(self.screen, GREEN, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 3)
        again_text = self.font_medium.render("Play Again", True, BLACK)
        again_rect = again_text.get_rect(center=button_rect.center)
        self.screen.blit(again_text, again_rect)

        leaderboard_rect = pygame.Rect(400, 570, 400, 60)
        pygame.draw.rect(self.screen, PURPLE, leaderboard_rect)
        pygame.draw.rect(self.screen, BLACK, leaderboard_rect, 3)
        leaderboard_text = self.font_small.render("View Leaderboard", True, WHITE)
        leaderboard_text_rect = leaderboard_text.get_rect(center=leaderboard_rect.center)
        self.screen.blit(leaderboard_text, leaderboard_text_rect)

        menu_rect = pygame.Rect(400, 640, 400, 60)
        pygame.draw.rect(self.screen, BLUE, menu_rect)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3)
        menu_text = self.font_small.render("Back to Menu", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)

    def handle_feedback_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.waiting_for_esc:
                self.in_question = False

                if self.current_world == "overworld":
                    current_time = pygame.time.get_ticks()
                    self.last_item_spawn_time = current_time - self.question_start_item_time

                if self.health <= 0:
                    self._handle_death()
                elif self.current_world == "overworld":
                    self.state = GameState.OVERWORLD
                elif self.current_world == "nether":
                    self.state = GameState.NETHER
                elif self.current_world == "end":
                    self.state = GameState.END

                    if isinstance(self.end_crystal_answered, list) and len(self.end_crystal_answered) >= self.end_crystal_count:
                        self.state = GameState.RESULTS

                self.waiting_for_esc = False

    def handle_name_input_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if self.name_input_text.strip():
                    play_sound("click")
                    self.start_game()
            elif event.key == pygame.K_BACKSPACE:
                self.name_input_text = self.name_input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            elif len(self.name_input_text) < 20 and event.unicode.isprintable():
                self.name_input_text += event.unicode

    def handle_results_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if 400 <= mouse_pos[0] <= 800 and 500 <= mouse_pos[1] <= 560:
                play_sound("click")
                self._score_saved = False
                self.state = GameState.NAME_INPUT
                self.name_input_text = self.player_name
                self.name_input_active = True
            elif 400 <= mouse_pos[0] <= 800 and 570 <= mouse_pos[1] <= 630:
                play_sound("click")
                self.state = GameState.LEADERBOARD
            elif 400 <= mouse_pos[0] <= 800 and 640 <= mouse_pos[1] <= 700:
                play_sound("click")
                self._score_saved = False
                self.state = GameState.MENU

    def handle_leaderboard_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if 400 <= mouse_pos[0] <= 800 and 700 <= mouse_pos[1] <= 760:
                play_sound("click")
                self.state = GameState.MENU
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU

    def draw_name_input(self):
        self.screen.fill(LIGHT_BLUE)

        title = self.font_large.render("Enter Your Name", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        instruction = self.font_small.render("Type your name and press Enter to start", True, DARK_GRAY)
        inst_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(instruction, inst_rect)

        input_rect = pygame.Rect(300, 350, 600, 60)
        pygame.draw.rect(self.screen, WHITE, input_rect)
        pygame.draw.rect(self.screen, BLACK, input_rect, 3)

        display_text = self.name_input_text
        if self.name_input_active:
            if int(pygame.time.get_ticks() / 500) % 2:
                display_text += "|"

        if display_text:
            text_surface = self.font_medium.render(display_text, True, BLACK)
            text_rect = text_surface.get_rect(center=input_rect.center)
            self.screen.blit(text_surface, text_rect)
        else:
            placeholder = self.font_small.render("Your name here...", True, GRAY)
            placeholder_rect = placeholder.get_rect(center=input_rect.center)
            self.screen.blit(placeholder, placeholder_rect)

        hint = self.font_tiny.render("Press ESC to cancel", True, DARK_GRAY)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(hint, hint_rect)

    def draw_leaderboard(self):
        self.screen.fill(LIGHT_BLUE)

        title = self.font_large.render("Speedrun Leaderboard", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        self.leaderboard.load_scores()
        all_scores = self.leaderboard.scores
        speedrun_scores = [s for s in all_scores if s.get("topic") == "Speedrun"]
        speedrun_scores.sort(key=lambda x: x["score"])
        top_scores = speedrun_scores[:10]

        player_entry = None
        player_rank = None
        effective_name = (self.player_name or "").strip() or "Player"
        for i, s in enumerate(speedrun_scores):
            if (s.get("name", "") or "").strip() == effective_name:
                player_entry = s
                player_rank = i + 1
                break

        y_start = 200
        if not top_scores:
            no_scores = self.font_medium.render("No speedruns yet! Be the first!", True, DARK_GRAY)
            no_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, 400))
            self.screen.blit(no_scores, no_rect)
        else:
            header_y = 150
            header_text = self.font_small.render("Rank  Name              Time      Questions", True, BLACK)
            self.screen.blit(header_text, (100, header_y))
            pygame.draw.line(self.screen, BLACK, (100, header_y + 30), (1100, header_y + 30), 2)

            for i, score_entry in enumerate(top_scores):
                y_pos = y_start + i * 40
                rank = i + 1
                name = score_entry["name"][:15]
                time_seconds = score_entry["score"]
                minutes = int(time_seconds // 60)
                seconds = int(time_seconds % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                questions = score_entry.get("questions_answered", 0)

                is_current_player = (score_entry.get("name", "") or "").strip() == effective_name
                if is_current_player:
                    highlight_rect = pygame.Rect(90, y_pos - 5, 1020, 35)
                    pygame.draw.rect(self.screen, YELLOW, highlight_rect)

                rank_text = self.font_small.render(f"{rank}.", True, BLACK)
                self.screen.blit(rank_text, (100, y_pos))
                name_text = self.font_small.render(name, True, BLACK)
                self.screen.blit(name_text, (150, y_pos))
                time_text = self.font_small.render(time_str, True, BLACK)
                self.screen.blit(time_text, (350, y_pos))
                questions_text = self.font_tiny.render(f"{questions} questions", True, DARK_GRAY)
                self.screen.blit(questions_text, (500, y_pos))

        if player_entry and player_entry not in top_scores and player_rank is not None:
            sep_y = y_start + len(top_scores) * 40 + 20 if top_scores else 250
            sep_text = self.font_small.render("\u2014\u2014\u2014 Your Rank \u2014\u2014\u2014", True, DARK_GRAY)
            self.screen.blit(sep_text, (100, sep_y))
            py = sep_y + 35
            time_seconds = player_entry["score"]
            minutes = int(time_seconds // 60)
            seconds = int(time_seconds % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            qs = player_entry.get("questions_answered", 0)
            your_text = self.font_small.render(
                f"#{player_rank}  {player_entry['name'][:15]}  {time_str}  {qs} questions",
                True, BLACK)
            your_rect = pygame.Rect(90, py - 5, 1020, 35)
            pygame.draw.rect(self.screen, YELLOW, your_rect)
            self.screen.blit(your_text, (100, py))

        back_rect = pygame.Rect(400, 700, 400, 60)
        pygame.draw.rect(self.screen, BLUE, back_rect)
        pygame.draw.rect(self.screen, BLACK, back_rect, 3)
        back_text = self.font_small.render("Back to Menu", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

    def draw(self):
        self.screen.fill(BLACK)
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.NAME_INPUT:
            self.draw_name_input()
        elif self.state == GameState.OVERWORLD:
            self.draw_overworld()
        elif self.state == GameState.NETHER:
            self.draw_nether()
        elif self.state == GameState.END:
            self.draw_end()
        elif self.state == GameState.QUESTION:
            self.draw_question()
        elif self.state == GameState.FEEDBACK:
            self.draw_feedback()
        elif self.state == GameState.RESULTS:
            self.draw_results()
        elif self.state == GameState.LEADERBOARD:
            self.draw_leaderboard()
        if self.show_return_to_lobby_prompt:
            self._draw_return_to_lobby_prompt()
        pygame.display.flip()

    def _handle_return_to_lobby_prompt(self, event):
        if not self.show_return_to_lobby_prompt:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                play_sound("click")
                self.show_return_to_lobby_prompt = False
                return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            box_y = (SCREEN_HEIGHT - 200) // 2
            yes_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, box_y + 130, 140, 50)
            no_rect = pygame.Rect(SCREEN_WIDTH // 2 + 40, box_y + 130, 140, 50)
            if yes_rect.collidepoint(mouse_pos):
                play_sound("click")
                self.show_return_to_lobby_prompt = False
                self._stop_lobby_music()
                self._lobby_music_started = False
                self.state = GameState.MENU
                return True
            if no_rect.collidepoint(mouse_pos):
                play_sound("click")
                self.show_return_to_lobby_prompt = False
                return True
        return False

    def _draw_return_to_lobby_prompt(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        box_w, box_h = (400, 200)
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        pygame.draw.rect(self.screen, (60, 50, 80), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, (120, 100, 160), (box_x, box_y, box_w, box_h), 3)
        msg = self.font_medium.render("Return to Lobby?", True, WHITE)
        self.screen.blit(msg, (box_x + (box_w - msg.get_width()) // 2, box_y + 40))
        hint = self.font_small.render("Your progress will not be saved.", True, (200, 180, 220))
        self.screen.blit(hint, (box_x + (box_w - hint.get_width()) // 2, box_y + 100))
        yes_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, box_y + 130, 140, 50)
        no_rect = pygame.Rect(SCREEN_WIDTH // 2 + 40, box_y + 130, 140, 50)
        pygame.draw.rect(self.screen, GREEN, yes_rect)
        pygame.draw.rect(self.screen, (50, 120, 50), yes_rect, 2)
        yes_text = self.font_small.render("Yes", True, WHITE)
        self.screen.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
        pygame.draw.rect(self.screen, RED, no_rect)
        pygame.draw.rect(self.screen, (150, 50, 50), no_rect, 2)
        no_text = self.font_small.render("No", True, WHITE)
        self.screen.blit(no_text, no_text.get_rect(center=no_rect.center))

    def run(self):
        running = True
        _game_states = (GameState.OVERWORLD, GameState.NETHER, GameState.END,
                        GameState.QUESTION, GameState.FEEDBACK, GameState.RESULTS)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self._handle_return_to_lobby_prompt(event):
                    continue
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_BACKQUOTE, pygame.K_p):
                    if self.state in _game_states:
                        self.show_return_to_lobby_prompt = True
                    continue
                if event.type == pygame.KEYDOWN and event.mod & pygame.KMOD_CTRL:
                    if event.key == pygame.K_8:
                        if self.state not in _game_states:
                            self.player_name = self.player_name or "Debug"
                            self.start_game()
                        self.state = GameState.OVERWORLD
                        self.current_world = "overworld"
                        self.current_biome = "alpine"
                        self._generate_alpine_platforms()
                        if self.alpine_platforms:
                            px, py, pw, ph = self.alpine_platforms[0]
                            self.player_x = px + pw // 2 - 10
                            self.player_y = float(py)
                        else:
                            self.player_x = SCREEN_WIDTH // 2
                            self.player_y = float(self.ground_y)
                        self.player_vy = 0.0
                        self.on_ground = True
                        self._fall_peak_y = None
                        self._biome_enter_time = pygame.time.get_ticks()
                        continue
                    elif event.key == pygame.K_9:
                        if self.state not in _game_states:
                            self.player_name = self.player_name or "Debug"
                            self.start_game()
                        self.state = GameState.END
                        self.current_world = "end"
                        self.in_question = False
                        self.player_x = SCREEN_WIDTH // 2
                        self.player_y = float(self.ground_y)
                        self.player_vy = 0.0
                        self.on_ground = True
                        self._init_end_crystals()
                        continue
                    elif event.key == pygame.K_0:
                        if self.state not in _game_states:
                            self.player_name = self.player_name or "Debug"
                            self.start_game()
                        self.state = GameState.NETHER
                        self.current_world = "nether"
                        self.in_question = False
                        self.player_x = SCREEN_WIDTH // 2
                        self.player_y = float(self.ground_y)
                        self.player_vy = 0.0
                        self.on_ground = True
                        self.piglin_fortress_questions = 0
                        self.nether_fortress_questions = 0
                        continue
                if self.state == GameState.MENU:
                    self.handle_menu_events(event)
                elif self.state == GameState.NAME_INPUT:
                    self.handle_name_input_events(event)
                elif self.state == GameState.OVERWORLD:
                    self.handle_overworld_events(event)
                elif self.state == GameState.NETHER:
                    self.handle_nether_events(event)
                elif self.state == GameState.END:
                    self.handle_end_events(event)
                elif self.state == GameState.QUESTION:
                    self.handle_question_events(event)
                elif self.state == GameState.FEEDBACK:
                    self.handle_feedback_events(event)
                elif self.state == GameState.RESULTS:
                    self.handle_results_events(event)
                elif self.state == GameState.LEADERBOARD:
                    self.handle_leaderboard_events(event)
            try:
                self.update()
                self.draw()
            except Exception as e:
                print(f"[Game Error] {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()



if __name__ == '__main__':
    game = ScienceGame()
    game.run()
