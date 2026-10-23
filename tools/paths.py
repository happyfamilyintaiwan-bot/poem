"""每首詩的輸出資料夾：out/年/月/編號/（2026-10-22 Zoe 指定：依詩的編號分月份，年份 2027）"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YEAR = '2027'


def out_dir(pid, *sub):
    """例：out_dir('0115', 'video') → out/2027/01/0115/video"""
    return os.path.join(ROOT, 'out', YEAR, pid[:2], pid, *sub)
