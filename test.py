"""
Samsung S23 Ultra 一键生成 QyzROM
国行
"""

from src.device import general

from tikpath import TikPath

tikpath = TikPath()
tikpath.set_project("TEST")


general.deal_with_vboot()