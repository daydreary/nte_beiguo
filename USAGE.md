# 用法说明

本文档说明如何从零配置并运行 `nte_autobeiguo` 自动化脚本。

## 快速开始

```bash
# 1. 克隆或下载项目
cd /path/to/nte_autobeiguo

# 2. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 确认 ADB 已连接模拟器
adb devices

# 5. 修改 adb_automsg.py 中的配置（见下文）

# 6. 运行
python adb_automsg.py
```

---

## 脚本说明

| 文件 | 作用 |
|------|------|
| `adb_automsg.py` | 主入口，负责 ADB 操作、页面判断与自动化流程 |
| `image_detector.py` | 图像识别库，基于 OpenCV 模板匹配定位 UI 元素 |
| `image_template/` | 各页面 UI 元素的模板截图 |

两个脚本的关系：`adb_automsg.py` 导入 `image_detector.detect_once()`，截图后调用模板匹配获取按钮坐标，再通过 ADB 执行点击。

---

## 自动化流程

脚本启动后会进入无限循环，根据当前页面自动跳转并执行任务：

```
                    ┌─────────────┐
                    │  启动脚本    │
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
              ┌────│  截图 + 识别  │────┐
              │    │  当前页面    │    │
              │    └─────────────┘    │
              ▼                       ▼
        send 页面              beiguo 页面
    （执行自动任务）           （点击进入发送页）
              │                       │
              ▼                       ▼
    entry_list 页面            input / submit 页面
    （进入列表）               （关闭弹窗返回）
              │                       │
              └───────────┬───────────┘
                          ▼
                   其他 / 未知页面
                   （点击入口进入列表）
```

### 各页面行为

| 识别结果 | 含义 | 脚本动作 |
|----------|------|----------|
| `send` | 发送/主操作页 | 滑动列表 → 查找帖子 → 点赞、收藏、评论 |
| `beiguo` | 备果相关页 | 点击「前往」按钮 |
| `entry_list` | 入口列表页 | 滚动查找目标条目并进入 |
| `input` / `submit` | 输入框或提交弹窗 | 关闭弹窗返回 |
| `None`（未识别） | 未知页面 | 点击入口坐标 `POS_ENTRY` |

### `send` 页面自动任务详情

在 `send` 页面时，脚本会依次执行：

1. 在屏幕中央向下滑动，加载更多内容；
2. 截图并在列表中查找 `like.png` 模板（最多 4 个匹配）；
3. 对每个匹配项点击进入详情；
4. 在详情页尝试：
   - 长按点赞按钮（`click_like.png`）
   - 长按收藏按钮（`collect.png`）
   - 长按评论输入框（`input.png`）→ 输入 `AUTO_INPUT_TEXT` → 点击完成 → 点击发送
5. 关闭详情页，继续处理下一个匹配项。

---

## 配置项说明

所有配置均在 `adb_automsg.py` 文件顶部，运行前请按你的环境修改。

### ADB 设备

```python
ADB_SERIAL = "127.0.0.1:16384"
```

| 值 | 说明 |
|----|------|
| `"127.0.0.1:16384"` | 连接指定模拟器（地址以 `adb devices` 为准） |
| `""` | 使用 adb 默认设备 |

常见模拟器 ADB 端口（仅供参考，以实际 `adb devices` 输出为准）：

| 模拟器 | 常见地址 |
|--------|----------|
| MuMu 模拟器 | `127.0.0.1:16384` / `127.0.0.1:7555` |
| 夜神模拟器 | `127.0.0.1:62001` |
| 雷电模拟器 | `127.0.0.1:5555` |

若设备未显示，可尝试：

```bash
adb connect 127.0.0.1:端口号
```

### 固定坐标

以下坐标需根据你的**模拟器分辨率**和 **App 布局**自行测量：

```python
POS_ENTRY = (1607, 50)           # 入口按钮
POS_ENTRY_SCROLL = (169, 537)    # 入口列表滚动区域
POS_GO = (1700, 1000)            # 「前往」按钮
POS_SCROLL_CENTER = (1067, 709)  # 主列表滚动区域
POS_CLOSE = (1835, 60)           # 关闭按钮
POS_INPUT_COMPLETE = (1695, 1045)  # 输入完成按钮
POS_INPUT_SEND = (1747, 969)     # 发送按钮
```

**获取坐标的方法：**

1. 在模拟器中开启「指针位置」或「开发者选项 → 显示触摸操作」；
2. 点击目标位置，记录状态栏或 logcat 中的 `(x, y)`；
3. 或使用 Android Studio 的 Layout Inspector / 第三方坐标工具。

### 模板图片路径

```python
TEMPLATE_ENTRY_LIST = "image_template/entry_list.png"
TEMPLATE_LIKE = "image_template/like.png"
TEMPLATE_CLICK_LIKE = "image_template/click_like.png"
TEMPLATE_COLLECT = "image_template/collect.png"
TEMPLATE_INPUT = "image_template/input.png"
TEMPLATE_SEND = "image_template/send.png"
TEMPLATE_BEIGUO_PAGE = "image_template/beiguo.png"
TEMPLATE_SUBMIT = "image_template/submit.png"
```

### 其他参数

```python
TAP_DURATION_MS = 50              # 点击持续时间（毫秒）
SCREENSHOT_PATH = "screen_tmp.png"  # 临时截图保存路径
AUTO_INPUT_TEXT = "哈哈哈，还挺好的"  # 自动评论内容
```

模板匹配默认阈值 `0.82`，在 `detect_once()` 调用处修改。

---

## 制作模板图片

模板图质量直接影响识别准确率，请按以下步骤制作：

1. 将模拟器调整到目标分辨率（建议固定，不要中途更改）；
2. 打开 App 到对应页面；
3. 执行截图：

```bash
adb -s 127.0.0.1:16384 exec-out screencap -p > screen_tmp.png
```

4. 用图片编辑工具裁剪出**特征明显、尺寸尽量小**的 UI 区域；
5. 保存为 `image_template/` 下对应文件名（如 `like.png`）；
6. 用下方「调试模板匹配」步骤验证是否能正确识别。

**注意：**

- 模板图应与模拟器当前主题、字体、分辨率一致；
- 避免包含过多背景，否则容易误匹配；
- 页面改版后需重新截取模板。

---

## 调试模板匹配

在正式运行主脚本前，建议先单独验证模板是否能匹配。

### 步骤 1：获取截图

```bash
adb -s 127.0.0.1:16384 exec-out screencap -p > screen_tmp.png
```

### 步骤 2：运行检测脚本

在项目目录下执行：

```bash
python -c "
from image_detector import detect_once

matches = detect_once(
    template_path='image_template/like.png',
    screenshot_path='screen_tmp.png',
    threshold=0.82,
    result_count=4,
)
print(f'匹配数量: {len(matches)}')
for i, m in enumerate(matches):
    print(f'  [{i}] center={m[\"center\"]}, score={m[\"score\"]:.3f}')
"
```

### 步骤 3：调整阈值

| 现象 | 建议 |
|------|------|
| 完全匹配不到 | 降低 `threshold`（如 `0.75`），或重新制作模板 |
| 误匹配过多 | 提高 `threshold`（如 `0.88`），或缩小模板区域 |
| 分数接近但不稳定 | 重新截取更清晰的模板 |

---

## 运行与停止

### 正常运行

```bash
source .venv/bin/activate
python adb_automsg.py
```

控制台输出示例：

```
检查 adb 连接状态...
3秒后开始执行...
脚本已启动，按 Ctrl + C 手动停止。
当前所在页面: send
找到列表item位置 320 , 580
找到点赞位置 150 , 920
...
```

### 停止脚本

在终端按 `Ctrl + C` 即可安全退出。

### 运行前检查清单

- [ ] 虚拟环境已激活，`pip install -r requirements.txt` 已执行
- [ ] `adb devices` 显示目标设备为 `device` 状态
- [ ] `ADB_SERIAL` 与设备地址一致
- [ ] 模拟器已打开目标 App 并处于可操作状态
- [ ] `image_template/` 模板图已从当前环境重新制作
- [ ] 固定坐标 `POS_*` 已按当前分辨率校准

---

## 常见问题

### 脚本报 `未找到在线设备`

```bash
adb kill-server
adb start-server
adb devices
```

确认设备地址后更新 `ADB_SERIAL`。

### 页面识别一直是 `None`

- 检查 `image_template/` 下 `send.png`、`beiguo.png` 等是否存在；
- 用「调试模板匹配」验证各页面模板；
- 确认模拟器分辨率与制作模板时一致。

### 能识别页面但点击位置不对

- 重新校准 `POS_*` 固定坐标；
- 模板匹配的 `center` 坐标一般较准，固定坐标偏差不影响模板定位的点击。

### 输入文字乱码或失败

- `input_text()` 通过 `adb shell input text` 输入，对中文支持因模拟器而异；
- 可尝试改用纯英文测试，或调整 `AUTO_INPUT_TEXT`。

---

## 进阶：单独使用 image_detector

`image_detector.py` 可作为独立模块在其他脚本中引用：

```python
from image_detector import detect_once

# 在已有截图上查找模板
results = detect_once(
    template_path="image_template/collect.png",
    screenshot_path="screen_tmp.png",
    threshold=0.82,
    result_count=2,
)

for item in results:
    x, y = item["center"]
    print(f"中心点: ({x}, {y}), 置信度: {item['score']:.2f}")
```

返回值字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `top_left` | `(x, y)` | 匹配区域左上角坐标 |
| `bottom_right` | `(x, y)` | 匹配区域右下角坐标 |
| `center` | `(x, y)` | 匹配区域中心点（常用于点击） |
| `score` | `float` | 匹配置信度，范围 0~1 |
