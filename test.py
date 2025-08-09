"""
Samsung S23 Ultra 一键生成 QyzROM
国行
"""

from tikpath import TikPath
from src.device import general

tikpath = TikPath()
tikpath.set_project("UI7")

# 2.4 处理vendor_boot
general.deal_with_vboot(remove_encryption=True)
