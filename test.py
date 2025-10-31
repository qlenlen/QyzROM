"""
Samsung S23 Ultra 一键生成 QyzROM
国行
"""

import os
import pathlib
import shutil

from src.custom import lp
from src.custom.ModuleDealer import ModuleDealer
from src.custom.ProductDealer import ProductDealer
from src.custom.SystemDealer import SystemDealer
from src.custom.VendorDealer import VendorDealer
from src.custom.XmlEditor import FFEditor
from src.image.Image import MyImage
from src.image.ImageConverter import ImageConverter
from tikpath import TikPath
from src.device import general


tikpath = TikPath()
tikpath.set_project("TEST")

MyImage("super").unpack()
qti_size = lp.get_qti_dynamic_partitions_size()
device_size = lp.get_device_size()
MyImage("super").unlink()

img_vendor = MyImage("vendor")
img_vendor.unpack()
VendorDealer().perform_slim()
img_vendor.pack_erofs().out2super()
img_vendor.unlink().rm_content()

img_system = MyImage("system")
img_system.unpack()
SystemDealer(version="V1.1").perform_slim("chn")
ModuleDealer("Media").perform_task()
ModuleDealer("Binary").perform_task()
ModuleDealer("Fonts").perform_task()
ModuleDealer("OneDesign").perform_task()
ModuleDealer("Preload").perform_task()
ModuleDealer("TgyStuff").perform_task()
ModuleDealer("BriefSupport").perform_task()

RUN_EXTRA_STEPS = os.getenv("RUN_EXTRA_STEPS") == "1"

if RUN_EXTRA_STEPS:
    img_system.unlink().rm_content()

img_product = MyImage("product")
img_product.unpack()
ProductDealer().perform_slim("chn")
img_product.pack_erofs().out2super()
if RUN_EXTRA_STEPS:
    img_product.unlink().rm_content()

MyImage("system_ext").unpack().pack_erofs().out2super()
if RUN_EXTRA_STEPS:
    shutil.rmtree(tikpath.get_content_path("system_ext"))
img_system.pack_ext().out2super()
MyImage("odm").move2super()
MyImage("system_dlkm").move2super()

img_vendor_dlkm = MyImage("vendor_dlkm").unpack()
ModuleDealer("BatteryKO").perform_task()
img_vendor_dlkm.pack_erofs().out2super()
img_vendor_dlkm.unlink().rm_content()

sh = lp.make_sh(tikpath.super, device_size, qti_size)
lp.cook(sh, tikpath.super)
# 清理super目录 只保留super.img
if RUN_EXTRA_STEPS:
    for item in pathlib.Path(tikpath.super).iterdir():
        if not item.name.startswith("super"):
            if not item.is_dir():
                item.unlink()
ImageConverter(f"{tikpath.super}/super.img").lz4_compress(need_remove_old=True)
