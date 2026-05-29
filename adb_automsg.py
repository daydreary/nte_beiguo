import time
import random
import subprocess
import shlex
import os
import json
import argparse
from typing import Union, List, Dict, Tuple

from image_detector import detect_once


# =========================
# ADB 配置
# =========================
# 可选：指定设备序列号（如 emulator-5554 / 127.0.0.1:5555）
# 不填则使用 adb 当前默认设备
ADB_SERIAL = "127.0.0.1:16384"

# 点击持续时间（毫秒）
TAP_DURATION_MS = 50

# =========================
# 动作坐标定义（你自行设置）
# =========================
# 示例坐标，请替换成你的模拟器按钮位置
POS_ENTRY = (1607, 50)
POS_ENTRY_SCROLL = (169, 537)
POS_GO = (1700, 1000)
POS_SCROLL_CENTER = (1067, 709)
POS_CLOSE = (1835, 60)
POS_INPUT_COMPLETE = (1695, 1045)
POS_INPUT_SEND = (1747, 969)

TEMPLATE_ENTRY_LIST = "image_template/entry_list.png"
TEMPLATE_LIKE = "image_template/like.png"
TEMPLATE_CLICK_LIKE = "image_template/click_like.png"
TEMPLATE_COLLECT = "image_template/collect.png"
TEMPLATE_INPUT = "image_template/input.png"

TEMPLATE_SEND = "image_template/send.png"
TEMPLATE_BEIGUO_PAGE = "image_template/beiguo.png"
TEMPLATE_SUBMIT = "image_template/submit.png"

SCREENSHOT_PATH = "screen_tmp.png"

AUTO_INPUT_TEXT = "哈哈哈，还挺好的"

def adb_prefix() -> str:
    if ADB_SERIAL.strip():
        return f"adb -s {shlex.quote(ADB_SERIAL)}"
    return "adb"


def run_cmd(cmd: str):
    """执行命令，失败时抛异常"""
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def check_adb_ready():
    """检查 adb 和目标设备是否可用"""
    run_cmd("adb start-server")
    if ADB_SERIAL.strip():
        # 检查指定设备是否在线
        out = subprocess.check_output("adb devices", shell=True, text=True)
        if f"{ADB_SERIAL}\tdevice" not in out:
            raise RuntimeError(f"未找到在线设备: {ADB_SERIAL}\n请确认 adb devices 输出。")
    else:
        # 未指定序列号时，至少要有 1 台在线设备
        out = subprocess.check_output("adb devices", shell=True, text=True)
        online = [line for line in out.splitlines()[1:] if line.strip().endswith("\tdevice")]
        if not online:
            raise RuntimeError("未检测到在线设备，请先连接模拟器并确保 adb devices 可见。")


def tap(pos: tuple[int, int]):
    x, y = pos
    cmd = f'{adb_prefix()} shell input tap {x} {y}'
    run_cmd(cmd)

def long_tap(pos: tuple[int, int], time : int):
    x, y = pos
    cmd = f'{adb_prefix()} shell input swipe {x} {y} {x} {y} {time}'
    run_cmd(cmd)

def scroll(pos: tuple[int, int], time : int, distance: int = -300):
    x, y = pos
    cmd = f'{adb_prefix()} shell input swipe {x} {y} {x} {y + distance} {time}'
    run_cmd(cmd)


def script_dir() -> str:
    """当前脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))


def take_screenshot(filename: str = SCREENSHOT_PATH) -> str:
    """
    通过 adb 截取设备屏幕，保存到脚本所在目录。

    :param filename: 截图文件名或绝对路径，默认使用 SCREENSHOT_PATH
    :return: 截图的绝对路径
    """
    save_path = filename if os.path.isabs(filename) else os.path.join(script_dir(), filename)
    cmd = f"{adb_prefix()} exec-out screencap -p"
    with open(save_path, "wb") as f:
        subprocess.run(cmd, shell=True, check=True, stdout=f)
    return save_path


def _escape_adb_input_text(text: str) -> str:
    """为 adb shell input text 转义特殊字符。"""
    mapping = {
        " ": "%s",
        "%": "%%",
        "&": "\\&",
        "<": "\\<",
        ">": "\\>",
        "|": "\\|",
        "(": "\\(",
        ")": "\\)",
        ";": "\\;",
        "*": "\\*",
        "`": "\\`",
        "\\": "\\\\",
        '"': '\\"',
        "'": "\\'",
        "$": "\\$",
    }
    return "".join(mapping.get(ch, ch) for ch in text)


def _clear_input_text(max_chars: int = 200):
    """清空当前聚焦输入框中的已有内容。"""
    cmd = ["adb"]
    if ADB_SERIAL.strip():
        cmd.extend(["-s", ADB_SERIAL])
    cmd.extend([
        "shell",
        f"input keyevent 123; for i in $(seq 1 {max_chars}); do input keyevent 67; done",
    ])
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def input_text(text: str):
    """
    假设输入框已弹起并聚焦，通过 adb 输入文本。
    若输入框内已有内容，会先清空再输入。

    :param text: 要输入的内容
    """
    _clear_input_text()
    escaped = _escape_adb_input_text(text)
    shell_safe = escaped.replace("'", "'\\''")
    cmd = f"{adb_prefix()} shell input text '{shell_safe}'"
    run_cmd(cmd)

def where_am_i() -> str:
    screenshot_where = take_screenshot()
    matches1 = detect_once(
        template_path=script_dir() + "/" + TEMPLATE_SEND,
        screenshot_path=screenshot_where,
        threshold=0.82,
        result_count=1
    )
    matches2 = detect_once(
        template_path=script_dir() + "/" + TEMPLATE_BEIGUO_PAGE,
        screenshot_path=screenshot_where,
        threshold=0.82,
        result_count=1
    )
    matches3 = detect_once(
            template_path=script_dir() + "/" + TEMPLATE_ENTRY_LIST,
            screenshot_path=screenshot_where,
            threshold=0.82,
            result_count=1
        )
    matches4 = detect_once(
            template_path=script_dir() + "/" + TEMPLATE_INPUT,
            screenshot_path=screenshot_where,
            threshold=0.82,
            result_count=1
        )
    matches5 = detect_once(
            template_path=script_dir() + "/" + TEMPLATE_SUBMIT,
            screenshot_path=screenshot_where,
            threshold=0.82,
            result_count=1
        )
    if matches1:
        return "send"
    elif matches2:
        return "beiguo"
    elif matches3:
        return "entry_list"
    elif matches4:
        return "input"
    elif matches5:
        return "submit"
    return None

def do_auto_work():
    scroll(POS_SCROLL_CENTER, 1000, -400)
    time.sleep(2)

    find_item = take_screenshot()
    items = detect_once(
        template_path=script_dir() + "/" + TEMPLATE_LIKE,
        screenshot_path=find_item,
        threshold=0.82,
        result_count=4
    )
    if items:
        for item in items:
            point_center = item["center"]
            tap(point_center)
            time.sleep(2)
            print(f"找到列表item位置 {point_center[0]} , {point_center[1]} ")

            do_action = take_screenshot()
            do_like = detect_once(
                template_path=script_dir() + "/" + TEMPLATE_CLICK_LIKE,
                screenshot_path=do_action,
                threshold=0.82
            )
            do_collect = detect_once(
                template_path=script_dir() + "/" + TEMPLATE_COLLECT,
                screenshot_path=do_action,
                threshold=0.82
            )
            do_input = detect_once(
                template_path=script_dir() + "/" + TEMPLATE_INPUT,
                screenshot_path=do_action,
                threshold=0.82
            )
            if do_like: 
                point_center = do_like[0]["center"]
                long_tap(point_center, 50)
                time.sleep(2)
                print(f"找到点赞位置 {point_center[0]} , {point_center[1]} ")
            if do_collect:
                point_center = do_collect[0]["center"]
                long_tap(point_center, 50)
                time.sleep(2)
                print(f"找到收藏位置 {point_center[0]} , {point_center[1]} ")
            if do_input:
                point_center = do_input[0]["center"]
                long_tap(point_center, 50)
                time.sleep(2)
                input_text(AUTO_INPUT_TEXT)
                time.sleep(2)
                long_tap(POS_INPUT_COMPLETE, 50)
                time.sleep(2)
                tap(POS_INPUT_SEND)
                time.sleep(2)
                print(f"找到输入位置 {point_center[0]} , {point_center[1]} ")
                    
            long_tap(POS_CLOSE, 50)
            time.sleep(2)

def go_to_send():
    tap(POS_GO)
    time.sleep(4)

def go_to_beiguo():
    while True:
        screenshot_entry_list = take_screenshot()
        matches = detect_once(
            template_path=script_dir() + "/" + TEMPLATE_ENTRY_LIST,
            screenshot_path=screenshot_entry_list,
            threshold=0.82,
            result_count=1
        )
        if matches:
            long_tap(matches[0]["center"], 50)
            time.sleep(2)
            break
        else:
            scroll(POS_ENTRY_SCROLL, 1000, -400)
            time.sleep(2)
            continue

def go_to_entry_list():
    tap(POS_ENTRY)
    time.sleep(2)

def back_to_send():
    long_tap(POS_CLOSE, 50)
    time.sleep(2)

def main():

    print("检查 adb 连接状态...")
    check_adb_ready()

    print("3秒后开始执行...")
    time.sleep(3)
    print("脚本已启动，按 Ctrl + C 手动停止。")

    while True:
        where = where_am_i()
        print(f"当前所在页面: {where}")
        if where == "send":
            do_auto_work();
        elif where == "beiguo":
            go_to_send();
        elif where == "entry_list":
            go_to_beiguo();
        elif where == "input" or where == "submit":
            back_to_send();
        else:
            go_to_entry_list();        


if __name__ == "__main__":
    main()
