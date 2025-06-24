"""
Samsung S23 Ultra 一键生成 QyzROM
国行
"""


from src.image.Image import MyImage
from tikpath import TikPath


from src.util.utils import MyPrinter

tikpath = TikPath()
tikpath.set_project("UI7")

myprinter = MyPrinter()

DEVICE = "dm3q"
AREA = "chn"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

ZIP_NAME = "S9180.zip"

vendor_image = MyImage("vendor")
vendor_image.unpack().pack_erofs()

