"""
Samsung S23 Ultra 一键生成 QyzROM
国行
"""

import os

from src.custom.CscEditor import CscEditor, get_csc_fp, get_ff_fp
from src.custom.ModuleDealer import ModuleDealer
from src.custom.ProductDealer import ProductDealer
from src.custom.SystemDealer import SystemDealer
from src.custom.VendorDealer import VendorDealer
from src.custom.XmlEditor import FFEditor
from src.device import general
from src.image.Image import MyImage
from src.image.ImageConverter import ImageConverter
from src.image.ImagePacker import ImagePacker
from src.image.ImageUnpacker import ImageUnpacker
from tikpath import TikPath
from src.custom import prepare, lp

from src.util.utils import MyPrinter

tikpath = TikPath()
tikpath.set_project("UI7")

myprinter = MyPrinter()

DEVICE = "dm3q"
AREA = "chn"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

ZIP_NAME = "S9180.zip"


# 2.4 处理vendor_boot
general.deal_with_vboot(remove_encryption=False)


