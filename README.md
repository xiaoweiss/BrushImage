# 星檬-工具箱

一个基于 **PySide6** 的桌面批处理工具箱（左侧工具列表 + 右侧参数页）。

当前内置工具：

- 图片尺寸调整（Pillow）
- 图片转换（Pillow）
- 音频转换（ffmpeg）
- MIDI 转 MusicXML（music21）

## 环境与依赖

- Python：建议 3.12
- 依赖管理：uv
- GUI：PySide6
- 图片处理：Pillow
- 音频处理：ffmpeg（需要本机可执行文件在 PATH 中，或后续自行打包附带）
- MIDI 处理：music21

## 开发运行（uv）

```bash
uv python install 3.12
uv venv --python 3.12
uv pip install -e .

# 启动（推荐）
uv run python -m atmob_pillow
```

也可以：

```bash
uv run python -m atmob_pillow.entrypoint
```

## 工具说明

### 1) 图片尺寸调整

- 输入：文件夹（只处理根目录，不递归）
- 输出：文件夹（不选则输出到当前工作目录）
- 参数：宽/高（强制拉伸到指定尺寸）、质量/压缩率
- 命名：`原文件名_resized.原扩展名`

### 2) 图片转换

- 输入：文件夹（只处理根目录，不递归）
- 参数：
  - 仅转换某些后缀（全部/仅 PNG/仅 JPG(JPEG)/自定义）
  - 输出格式（JPG/PNG/WEBP）
  - 质量/压缩率（1-100）
  - 并发数
- 处理规则：
  - PNG 转 JPG 时，如存在透明通道，会自动以白底合成，避免黑底/透明丢失异常。
- 命名：`原文件名.原扩展名_converted.目标扩展名`（包含源扩展名，避免同名冲突）

### 3) 音频转换（ffmpeg）

- 输入：文件夹（只处理根目录，不递归）
- 输出格式：支持多种扩展名（下拉选择）
- 支持参数：
  - 输入过滤（全部/仅 MP3/仅 WAV/自定义扩展名）
  - 剪切（开始/结束时间）
  - 编解码器
  - 声道
  - 频率（采样率）
  - 码率（下拉）
  - 音量（dB）
  - 并发数
- 命名：`原文件名.原扩展名_converted.目标扩展名`（包含源扩展名，避免同名冲突）

### 4) MIDI 转 MusicXML（music21）

- 输入：文件夹（只处理根目录，不递归）
- 输出：`.musicxml`
- 参数：
  - 量化模式（不量化/自动量化/八分/十六分/三十二分）
  - 去除小休止符
  - 并发数

## Windows 打包（GitHub Actions）

项目包含 Windows 打包 workflow（PyInstaller）。

- 触发方式：push tag（如 `v0.1.0`）或手动触发
- 产物：`dist/atmob-image.exe`（artifact 下载）

> 注意：如果你需要在 exe 内置 ffmpeg，需要额外把 ffmpeg.exe 一起打包/分发（当前默认依赖系统 PATH）。
