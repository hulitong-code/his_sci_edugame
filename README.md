# His Sci EduGame 2 — 历史科学教育游戏 2

> 一款以 Minecraft 为主题的科学知识竞答教育游戏  
> A Minecraft-themed science quiz educational game

---

## 目录 / Table of Contents

- [简介 / Introduction](#简介--introduction)
- [游戏截图 / Screenshots](#游戏截图--screenshots)
- [功能特性 / Features](#功能特性--features)
- [环境要求 / Requirements](#环境要求--requirements)
- [安装与运行 / Installation & Running](#安装与运行--installation--running)
- [游戏玩法 / Gameplay](#游戏玩法--gameplay)
- [知识题库 / Question Bank](#知识题库--question-bank)
- [自定义扩展 / Customization](#自定义扩展--customization)
- [音频配置 / Audio Setup](#音频配置--audio-setup)
- [项目结构 / Project Structure](#项目结构--project-structure)

---

## 简介 / Introduction

**His Sci EduGame 2** 是一款专为中小学生设计的科学益智游戏，以 Minecraft 世界为舞台，通过答题收集资源、探索群系、挑战末地 Boss，让玩家在游戏中轻松掌握科学知识。

**His Sci EduGame 2** is a science quiz game designed for elementary and middle school students. Set in a Minecraft-style world, players answer science questions to collect resources, explore biomes, and challenge the End boss — learning science while having fun.

---

## 游戏截图 / Screenshots

> *(在此处添加游戏截图 / Add screenshots here)*

---

## 功能特性 / Features

### 中文

- **三大世界进阶**：主世界 → 下界 → 末地，层层递进
- **7 种生物群系**：森林、平原、沙漠、雪地、高山、海洋、恶地
- **动态难度调节**：根据答题表现自动升降难度（简单 / 中等 / 困难）
- **5 大科学主题**：水循环、物质状态、太阳系、植物、动物（约 90 道题）
- **资源收集机制**：正确答题获得黑曜石、末影珍珠、烈焰棒等资源
- **生命值系统**：面包、金苹果治疗，不死图腾复活
- **高分排行榜**：持久化存储，支持 Top 100
- **程序化音效**：正误反馈、跳跃、受伤等音效均由代码生成
- **背景音乐**：支持 Minecraft C418 系列 MP3 播放
- **图片题目支持**：题目可附带图片辅助说明

### English

- **Three-world progression**: Overworld → Nether → End
- **7 biomes**: Forest, Plains, Desert, Snow, Alpine, Ocean, Badlands
- **Dynamic difficulty**: Auto-adjusts based on performance (Easy / Medium / Hard)
- **5 science topics**: Water Cycle, States of Matter, Solar System, Plants, Animals (~90 questions)
- **Resource collection**: Earn obsidian, ender pearls, blaze rods by answering correctly
- **Health system**: Bread and golden apples heal; Totem of Undying revives
- **Leaderboard**: Persistent JSON storage, Top 100 scores
- **Procedural sound effects**: Correct/wrong answers, jump, hurt, etc., generated in code
- **Background music**: Supports Minecraft C418 MP3 playback
- **Image support**: Questions can include images

---

## 环境要求 / Requirements

| 项目 / Item | 要求 / Requirement |
|---|---|
| Python | 3.7 或更高 / 3.7 or higher |
| pygame | 最新稳定版 / Latest stable |
| 操作系统 / OS | Windows / macOS |
| 分辨率 / Resolution | 1200 × 800 或更高 / or higher |
| 音频文件 / Audio | 可选 / Optional |

---

## 安装与运行 / Installation & Running

### 中文

```bash
# 1. 克隆仓库
git clone https://github.com/<你的用户名>/his_sci_edugame2.git
cd his_sci_edugame2

# 2. 安装依赖
pip install pygame

# 3. 运行游戏
python src/main.py
```

### English

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/his_sci_edugame2.git
cd his_sci_edugame2

# 2. Install dependencies
pip install pygame

# 3. Run the game
python src/main.py
```

### 调试快捷键 / Debug Shortcuts

| 快捷键 / Shortcut | 功能 / Function |
|---|---|
| `Ctrl + 8` | 跳转到高山群系 / Jump to Alpine biome |
| `Ctrl + 9` | 跳转到末地 / Jump to End world |
| `Ctrl + 0` | 跳转到下界 / Jump to Nether |
| `` ` `` 或 / or `P` | 返回大厅提示 / Return to lobby |

---

## 游戏玩法 / Gameplay

### 中文

1. **主菜单**：选择随机游戏、指定主题或查看排行榜
2. **输入姓名**：记录成绩需要玩家名称
3. **主世界**：探索群系，答题获得**黑曜石**（需 5 块进入下界）
4. **下界**：收集**末影珍珠**（3 个）和**烈焰棒**（3 根）进入末地
5. **末地**：摧毁 5 个末地水晶击败 Boss，赢得游戏
6. 答错扣除生命值（主世界 1 点 / 下界 2 点 / 末地 4 点）
7. 每局共 20 道题，得分记入排行榜

### English

1. **Main Menu**: Choose random game, specific topic, or view leaderboard
2. **Enter name**: Required for score tracking
3. **Overworld**: Explore biomes and earn **obsidian** (need 5 to enter Nether)
4. **Nether**: Collect **ender pearls** (3) and **blaze rods** (3) to enter the End
5. **End**: Destroy 5 end crystals to defeat the boss and win
6. Wrong answers reduce health (Overworld: 1 / Nether: 2 / End: 4 hearts)
7. Each run has 20 questions; scores are saved to the leaderboard

---

## 知识题库 / Question Bank

### 题目主题 / Topics

| 主题 / Topic | 文件 / File | 题目数 / Questions |
|---|---|---|
| 水循环 / Water Cycle | `water_cycle.txt` | 16 |
| 物质状态 / States of Matter | `states_of_matter.txt` | 18 |
| 太阳系 / Solar System | `solar_system.txt` | 19 |
| 植物 / Plants | `plants.txt` | 18 |
| 动物 / Animals | `animals.txt` | 19 |

### 题目格式 / Question Format

```
这道题的问题是什么？
a) 正确答案（a 选项始终为正确答案）
b) 错误选项
c) 错误选项
d) 错误选项
Image: optional_image.png
Explanation: 解释为什么 a 是正确答案

What is this question asking?
a) Correct answer (option a is ALWAYS correct in source)
b) Wrong option
c) Wrong option
d) Wrong option
Image: optional_image.png
Explanation: Why a is the correct answer
```

> **注意 / Note**：`a` 选项在源文件中始终为正确答案，游戏运行时选项顺序会自动打乱。  
> Option `a` in the source file is always the correct answer; options are shuffled at runtime.

详见 / See: [`src/questions/README.md`](src/questions/README.md)

---

## 自定义扩展 / Customization

### 添加题目 / Add Questions

**中文**：直接编辑 `src/questions/` 下对应的 `.txt` 文件，重启游戏即可生效。

**English**: Edit the corresponding `.txt` file in `src/questions/`, then restart the game.

### 添加新主题 / Add a New Topic

**中文**：

1. 在 `src/questions/` 创建 `新主题.txt`
2. 在 `src/questions.py` 的 `topic_files` 字典中添加新条目
3. 在 `src/main.py` 的 `topics` 列表中添加主题名称

**English**:

1. Create `new_topic.txt` in `src/questions/`
2. Add it to the `topic_files` dict in `src/questions.py`
3. Add the topic name to the `topics` list in `src/main.py`

### 添加图片题目 / Add Image Questions

**中文**：将图片（PNG/JPG/GIF/BMP）放入 `src/questions/images/`，在题目中添加 `Image: 文件名` 行。

**English**: Place images (PNG/JPG/GIF/BMP) in `src/questions/images/`, then add `Image: filename` line in the question file.

详见 / See: [`src/questions/IMAGE_SETUP_GUIDE.md`](src/questions/IMAGE_SETUP_GUIDE.md)

---

## 音频配置 / Audio Setup

**中文**：将以下 MP3 文件放入 `src/audio/` 目录（文件名需完全一致），游戏缺少音频文件时仍可正常运行。

**English**: Place the following MP3 files in `src/audio/` (exact filenames required). The game runs fine without audio files.

| 场景 / Scene | 文件名 / Filename |
|---|---|
| 大厅 / Lobby | `C418 - Minecraft - Minecraft Volume Alpha 4.mp3` |
| 游戏中 / Gameplay | `C418 - Subwoofer Lullaby - Minecraft Volume Alpha 4.mp3` |

详见 / See: [`src/audio/README.md`](src/audio/README.md)

---

## 项目结构 / Project Structure

```
his_sci_edugame2/
├── src/
│   ├── main.py              # 主游戏引擎 / Main game engine
│   ├── questions.py         # 题库加载器 / Question loader
│   ├── leaderboard.py       # 排行榜管理 / Leaderboard manager
│   ├── audio_utils.py       # 音频工具 / Audio utilities
│   ├── leaderboard.json     # 排行榜数据 / Leaderboard data
│   ├── questions/           # 题目文件 / Question files
│   │   ├── water_cycle.txt
│   │   ├── states_of_matter.txt
│   │   ├── solar_system.txt
│   │   ├── plants.txt
│   │   ├── animals.txt
│   │   ├── images/          # 题目图片 / Question images
│   │   ├── README.md
│   │   └── IMAGE_SETUP_GUIDE.md
│   └── audio/               # 背景音乐 / Background music
│       └── README.md
└── README.md
```

---

## 打包发布 / Building for Distribution

```bash
# 使用 PyInstaller 打包 / Package with PyInstaller
pip install pyinstaller
pyinstaller --onefile src/main.py
```

---

## 许可证 / License MIT

本项目仅供教育用途。Minecraft 相关元素版权归 Mojang/Microsoft 所有。  
This project is for educational purposes only. Minecraft-related elements are property of Mojang/Microsoft.
