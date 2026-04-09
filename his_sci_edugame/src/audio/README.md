# 音乐与音效设置说明 / Audio Setup Guide

## 如何导入音乐 / How to Add Music

### 1. 创建 audio 目录

在项目根目录下已有 `audio` 文件夹，将音乐文件放入此目录即可。

### 2. 大厅背景音乐

- **文件名**：`C418 - Minecraft - Minecraft Volume Alpha 4.mp3`
- **放置位置**：`his_sci_edugame/audio/C418 - Minecraft - Minecraft Volume Alpha 4.mp3`
- **格式**：支持 `.mp3`、`.ogg`、`.wav`

进入游戏大厅时会自动循环播放。若没有该文件，游戏照常运行，只是没有背景音乐。

### 3. 使用其他音乐文件

在代码中可调用：

```python
# 播放某首音乐，循环
self._load_and_play_music("菜单音乐", loop=-1, volume=0.5)

# 播放一次
self._load_and_play_music("过关音效", loop=0, volume=0.7)

# 停止背景音乐
self._stop_music()
```

对应文件需放在 `audio/` 下，例如：
- `audio/菜单音乐.ogg`
- `audio/过关音效.ogg`

### 4. 音效（可选扩展）

当前仅实现了背景音乐。若需按钮、答题等音效，可后续使用 `pygame.mixer.Sound("audio/click.ogg")` 加载并播放短音效。

### 5. 版权与格式建议

- 请使用您有权限使用的音乐（原创、CC 授权、免版税素材等）。
- 可到 [Pixabay](https://pixabay.com/music/)、[FreePD](https://freepd.com/) 等网站下载免费背景音乐。
- 若是 MP3/WAV，可用 [Audacity](https://www.audacityteam.org/) 等工具转换为 OGG 以减小体积。
