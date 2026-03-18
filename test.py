"""
Samsung S23 Ultra 一键生成 QyzROM
国行
"""

from src.device import general

from tikpath import TikPath
import re
import pathlib
import os

tikpath = TikPath()
tikpath.set_project("TEST")

extract_path = os.path.join(tikpath.project_path, "extracted")