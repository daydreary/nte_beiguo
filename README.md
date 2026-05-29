# nte_autobeiguo

基于 **ADB + OpenCV 模板匹配** 的 Android 模拟器自动化脚本，用于在指定 App 页面中自动完成点赞、收藏、评论等操作。

## 环境要求

| 依赖 | 说明 |
|------|------|
| Python | 3.9 及以上（推荐 3.10+） |
| ADB | Android Debug Bridge，需已加入系统 PATH |
| Android 模拟器 | 已开启 USB 调试，且 `adb devices` 可见 |

---

## 一、安装 Python

### macOS

```bash
# 方式 1：官网安装包
# 访问 https://www.python.org/downloads/ 下载并安装

# 方式 2：Homebrew
brew install python@3.12

# 验证
python3 --version
```

### Windows

1. 访问 [Python 官网](https://www.python.org/downloads/) 下载安装包；
2. 安装时勾选 **Add Python to PATH**；
3. 打开命令提示符或 PowerShell，验证：

```powershell
python --version
```

---

## 二、配置 Python 环境与 OpenCV

```bash
# 安装依赖
pip3 install -r requirements.txt
```

> **说明**：依赖见 `requirements.txt`（`opencv-python`、`numpy`）。若仅需 headless 环境（无 GUI），可将 `opencv-python` 替换为 `opencv-python-headless`。

---

## 三、安装与配置 ADB

### 安装 ADB

**macOS（Homebrew）：**

```bash
brew install android-platform-tools
```

**Windows：**

下载 [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools)，解压后将目录加入系统 PATH。

### 连接模拟器

1. 启动 Android 模拟器（如 MuMu、夜神、雷电等）；需要将模拟器设置为1920*1080平板模式；
2. 在模拟器设置中开启 **USB 调试**；
3. 确认设备在线：

```bash
adb devices
```

示例输出：

```
List of devices attached
127.0.0.1:16384    device
```

若显示 `unauthorized`，请在模拟器上允许 USB 调试授权后重试。

---

## 四、运行前配置

编辑 `adb_automsg.py` 顶部的配置项，使其与你的模拟器环境一致。

### 1. ADB 设备地址

```python
ADB_SERIAL = ""  # 改为 adb devices 中显示的设备地址
```

留空则使用 `adb` 默认设备：

```python
ADB_SERIAL = ""
```

### 2. 点击坐标

根据你的模拟器分辨率与 App 布局，修改以下坐标：

```python
POS_ENTRY = (1607, 50)
POS_ENTRY_SCROLL = (169, 537)
POS_GO = (1700, 1000)
POS_SCROLL_CENTER = (1067, 709)
POS_CLOSE = (1835, 60)
POS_INPUT_COMPLETE = (1695, 1045)
POS_INPUT_SEND = (1747, 969)
```

### 3. 自动评论文案

```python
AUTO_INPUT_TEXT = "哈哈哈，还挺好的"
```

### 4. 模板图片

`image_template/` 目录下的 PNG 需从**你自己的模拟器**中截取对应 UI 元素。分辨率或主题变化后，模板图需重新制作，否则匹配会失败。

模板匹配阈值默认为 `0.82`，可在代码中按需调整。

---

## 五、运行脚本

```bash
# 进入项目目录
cd /path/to/nte_autobeiguo

# 运行主脚本
python3 adb_automsg.py
```

运行流程：

1. 检查 ADB 与目标设备是否在线；
2. 等待 3 秒后开始执行；
3. 自动识别当前页面并执行对应操作；
4. 按 `Ctrl + C` 手动停止。

更详细的配置说明、页面流程、模板制作与调试方法，请参阅 **[USAGE.md](./USAGE.md)**。

---

## 六、单独测试图像检测

`image_detector.py` 也可独立用于调试模板匹配效果：

```python
from image_detector import detect_once

matches = detect_once(
    template_path="image_template/like.png",
    screenshot_path="screen_tmp.png",
    threshold=0.82,
    result_count=2,
)

for m in matches:
    print(m)
# 输出示例：{'top_left': (x, y), 'bottom_right': (x, y), 'center': (cx, cy), 'score': 0.91}
```

先用 `adb exec-out screencap -p > screen_tmp.png` 获取一张截图，再运行上述代码验证模板是否匹配。

---

## 常见问题

### `未找到在线设备`

- 确认模拟器已启动且 USB 调试已开启；
- 运行 `adb devices` 检查设备地址是否与 `ADB_SERIAL` 一致；
- 部分模拟器需手动连接：`adb connect 127.0.0.1:端口号`。

### `无法读取截图` / `无法读取模板图`

- 检查 `image_template/` 下对应 PNG 是否存在；
- 确认截图路径正确，且有读写权限。

### 模板匹配不到或误匹配

- 重新从当前模拟器截取模板图；
- 调低或调高 `threshold`（建议范围 `0.75 ~ 0.90`）；
- 确保模拟器分辨率、缩放比例与制作模板时一致。

### `import cv2` 报错

- 确认已在虚拟环境中安装：`pip install -r requirements.txt`；
- Python 版本建议 3.9 及以上。

---

## 项目结构

```
nte_autobeiguo/
├── adb_automsg.py      # 主脚本：ADB 控制、页面识别、自动化流程
├── image_detector.py   # 图像检测模块：OpenCV 模板匹配
├── image_template/     # 页面元素模板图（需与模拟器分辨率一致）
│   ├── send.png
│   ├── beiguo.png
│   ├── entry_list.png
│   ├── like.png
│   ├── click_like.png
│   ├── collect.png
│   ├── input.png
│   └── submit.png
├── requirements.txt    # Python 依赖
├── USAGE.md            # 详细用法说明
└── README.md
```

## 工作原理

1. 通过 `adb exec-out screencap` 截取模拟器屏幕；
2. `image_detector.py` 使用 OpenCV `matchTemplate` 在截图中查找模板图位置；
3. `adb_automsg.py` 根据识别结果判断当前页面，并执行点击、滑动、输入文本等操作；
4. 循环运行，直到手动按 `Ctrl + C` 停止。

## 免责声明

本工具仅供学习与技术研究使用。请遵守相关平台服务条款与法律法规，勿用于违规或滥用场景。使用本脚本产生的一切后果由使用者自行承担。
