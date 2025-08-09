"""
Samsung S23 Ultra 一键生成 QyzROM
国行
"""

from tikpath import TikPath
from src.device import general

tikpath = TikPath()
tikpath.set_project("UI7")

general.patch_lkm("android13-5.15")
