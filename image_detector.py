import subprocess
from typing import Dict, List, Tuple

import cv2
import numpy as np


def _match_template(
    screenshot_path: str,
    template_path: str,
    threshold: float,
    result_count: int = 2
) -> List[Dict[str, Tuple[int, int]]]:
    screen = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    if screen is None:
        raise FileNotFoundError(f"无法读取截图: {screenshot_path}")
    if template is None:
        raise FileNotFoundError(f"无法读取模板图: {template_path}")

    th, tw = template.shape[:2]
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

    ys, xs = np.where(result >= threshold)
    matches = []
    for x, y in zip(xs, ys):
        score = float(result[y, x])
        top_left = (int(x), int(y))
        bottom_right = (int(x + tw), int(y + th))
        center = (int(x + tw / 2), int(y + th / 2))
        matches.append({
            "top_left": top_left,
            "bottom_right": bottom_right,
            "center": center,
            "score": score
        })

    # 按分数降序，只返回前 n 个（不超过实际匹配数量）
    matches.sort(key=lambda m: m["score"], reverse=True)
    count = min(result_count, len(matches))
    return matches[:count]


def detect_once(
    template_path: str,
    screenshot_path: str,
    threshold: float = 0.82,
    result_count: int = 2
) -> List[Dict[str, Tuple[int, int]]]:
    """
    执行一次检测：模板匹配 -> 返回疑似区域数组

    :param template_path: 模板图片路径（如 1.png）
    :param screenshot_path: 截图保存路径（函数会覆盖该文件）
    :param threshold: 匹配阈值（0~1）
    :return: 疑似区域数组，元素示例：
             {
               "top_left": (x1, y1),
               "bottom_right": (x2, y2),
               "center": (cx, cy),
               "score": 0.91
             }
    """
    return _match_template(
        screenshot_path=screenshot_path,
        template_path=template_path,
        threshold=threshold,
        result_count=result_count
    )
