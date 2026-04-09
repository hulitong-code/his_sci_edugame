"""
音效工具，用来程序化生成音效，以及播放外部音频文件
支持：正确、错误、点击、跳跃、收集、完成、受伤。通过
程序化生成，使用 pygame.mixer.music 播放
"""
import math
import array
import os
from typing import Dict

def _make_tone(freq: float, duration: float = 0.15, volume: float = 0.3, sample_rate: int = 22050) -> bytes:
    """生成单一频率正弦波，返回 PCM 字节数据（16-bit mono）"""
    n_samples = int(sample_rate * duration)
    buf = array.array("h")
    for i in range(n_samples):
        t = i / sample_rate
        env = 1.0 if duration <= 0.1 else max(0, 1 - i / n_samples * 0.5)
        val = int(32767 * volume * env * math.sin(2 * math.pi * freq * t))
        buf.append(max(-32768, min(32767, val)))
    return buf.tobytes()

def _make_success_chord() -> bytes:
    """正确：叠加双音"""
    sr = 22050
    dur = 0.25
    n = int(sr * dur)
    buf = array.array("h", [0] * n)
    for i in range(n):
        t = i / sr
        env = 1 - i / n * 0.6
        f1, f2 = 523.25, 659.25
        v = int(6553.400000000001 * env * (math.sin(2 * math.pi * f1 * t) + math.sin(2 * math.pi * f2 * t)) / 2)
        buf[i] = max(-32768, min(32767, v))
    return buf.tobytes()

def _make_error_tone() -> bytes:
    """错误：低沉嗡鸣"""
    return _make_tone(180, 0.2, 0.25)

def _make_click() -> bytes:
    """点击/选择"""
    return _make_tone(600, 0.06, 0.2)

def _make_jump() -> bytes:
    """跳跃"""
    return _make_tone(400, 0.1, 0.25)

def _make_collect() -> bytes:
    """收集物品"""
    return _make_tone(880, 0.12, 0.3)

def _make_complete() -> bytes:
    """通关"""
    sr = 22050
    dur = 0.5
    n = int(sr * dur)
    buf = array.array("h", [0] * n)
    notes = [523.25, 659.25, 783.99, 1046.5]
    for i in range(n):
        t = i / sr
        idx = min(int(i / (n / 4)), 3)
        f = notes[idx]
        env = 0.8 - i / n * 0.5
        v = int(6553.400000000001 * env * math.sin(2 * math.pi * f * t))
        buf[i] = max(-32768, min(32767, v))
    return buf.tobytes()

def _make_hurt() -> bytes:
    """受伤"""
    return _make_tone(150, 0.15, 0.3)

def _make_heal() -> bytes:
    """使用回复物品或者生命恢复生命"""
    return _make_tone(660, 0.2, 0.25)

def _make_death() -> bytes:
    """死亡"""
    return _make_tone(120, 0.4, 0.35)

def _make_totem() -> bytes:
    """获得图腾加持"""
    sr = 22050
    dur = 0.35
    n = int(sr * dur)
    buf = array.array("h", [0] * n)
    for i in range(n):
        t = i / sr
        f = 400 + 200 * (i / n)
        env = 0.8 - i / n * 0.6
        v = int(6553.400000000001 * env * math.sin(2 * math.pi * f * t))
        buf[i] = max(-32768, min(32767, v))
    return buf.tobytes()

_sound_cache: Dict[str, "pygame.mixer.Sound"] = {}
_mixer_ready: bool = False

def init_audio() -> bool:
    """初始化 pygame.mixer"""
    global _mixer_ready
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        _mixer_ready = True
        return True
    except Exception:
        _mixer_ready = False
        return False

def _get_sound(name: str):
    """获取或生成音效"""

    if name in _sound_cache:
        return _sound_cache[name]
    if not _mixer_ready:
        return None
    try:
        import pygame
        generators = {
            'correct': _make_success_chord,
            'wrong': _make_error_tone,
            'click': _make_click,
            'jump': _make_jump,
            'collect': _make_collect,
            'complete': _make_complete,
            'hurt': _make_hurt,
            'heal': _make_heal,
            'death': _make_death,
            'totem': _make_totem,
        }
        if name not in generators:
            return None
        data = generators[name]()
        snd = pygame.mixer.Sound(buffer=data)
        _sound_cache[name] = snd
        return snd
    except Exception:
        return None

def play_sound(name: str, volume: float = 1.0) -> bool:
    """
    播放音效。name: correct, wrong, click, jump, collect, complete, hurt, heal, death, totem
    """
    snd = _get_sound(name)
    if snd is None:
        return False
    try:
        snd.set_volume(volume)
        snd.play()
        return True
    except Exception:
        return False


def play_music(filepath: str, loop: int = -1, volume: float = 0.5) -> bool:
    """
    使用 pygame.mixer.music 播放背景音乐。
    loop=-1 表示循环，loop=0 播放一次。
    """
    if not _mixer_ready or not filepath or not os.path.exists(filepath):
        return False
    try:
        import pygame
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)
        return True
    except Exception:
        return False


def stop_music() -> None:
    """停止背景音乐"""
    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass
