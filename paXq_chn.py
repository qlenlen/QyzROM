"""
Samsung S25 Ultra 一键生成 QyzROM
国行
"""

import os
import pathlib

RUN_EXTRA_STEPS = os.getenv("RUN_EXTRA_STEPS") == "1"

from src.custom.CscEditor import CscEditor, get_csc_fp, get_ff_fp
from src.custom.ModuleDealer import ModuleDealer
from src.custom.ProductDealer import ProductDealer
from src.custom.SystemDealer import SystemDealer
from src.custom.VendorDealer import VendorDealer
from src.custom.XmlEditor import FFEditor
from src.custom.lp import SuperType
from src.device import general
from src.image.Image import MyImage
from src.image.ImageConverter import ImageConverter
from tikpath import TikPath
from src.custom import prepare, lp

from src.util.utils import MyPrinter

tikpath = TikPath()
tikpath.set_project("pa3q")

myprinter = MyPrinter()

DEVICE = "pa3q"
AREA = "chn"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

ZIP_NAME = "S9380.zip"

general.clean()

# 1. 提取需要的文件
prepare.unarchive(skip_zip=False, remove_tars=RUN_EXTRA_STEPS)

# 2. 分门别类处理镜像
# 2.1 avb去除
general.deal_with_avb()

# 2.2 内核替换
pass

# 2.3 替换twrp
pass

# 2.4 处理vendor_boot
general.deal_with_vboot(remove_encryption=True)

# 2.5 处理optics
general.moveimg2project("CSC", "optics")
img_optics = MyImage("optics")
img_optics.unpack()
CscEditor(get_csc_fp("CHC")).perform_chn()
img_optics.pack_ext()
ImageConverter(img_optics.img_output).img2simg()

# 处理super
general.moveimg2project("AP", "super")
MyImage("super").unpack()
qti_size = lp.get_qti_dynamic_partitions_size()
device_size = lp.get_device_size()
if RUN_EXTRA_STEPS:
    MyImage("super").unlink()

img_product = MyImage("product_a")
img_product.unpack()
ProductDealer("product_a", "pa3q").perform_slim("chn")
img_product.pack_erofs().out2super()
if RUN_EXTRA_STEPS:
    img_product.unlink().rm_content()

img_vendor = MyImage("vendor_a")
img_vendor.unpack()
VendorDealer(is_aonly=False).fill_mount_point().remove_avb().remove_encryption()
img_vendor.pack_erofs().out2super()
if RUN_EXTRA_STEPS:
    img_vendor.unlink().rm_content()

img_system = MyImage("system_a")
img_system.unpack()
SystemDealer("system_a", "pa3q").perform_slim("chn")

ModuleDealer("Binary", is_vab=True).perform_task()
ModuleDealer("Fonts_V2", is_vab=True).perform_task()
ModuleDealer("Preload", is_vab=True).perform_task()
ModuleDealer("OneDesign", is_vab=True).perform_task()
ModuleDealer("TgyStuff", is_vab=True).perform_task()

FFEditor.from_toml(
    get_ff_fp(),
    f"{tikpath.res_path}/{DEVICE}/tasks/{AREA}/ff.toml",
).save_xml()

img_system.pack_ext().out2super()

if RUN_EXTRA_STEPS:
    img_system.unlink().rm_content()

MyImage("system_ext_a").move2super()
MyImage("odm_a").move2super()
MyImage("system_dlkm_a").move2super()
MyImage("vendor_dlkm_a").move2super()

sh = lp.make_sh(tikpath.super, device_size, qti_size, SuperType.VAB)
lp.cook(sh, tikpath.super)
# 清理super目录 只保留super.img
if RUN_EXTRA_STEPS:
    for item in pathlib.Path(tikpath.super).iterdir():
        if not item.name.startswith("super"):
            if not item.is_dir():
                item.unlink()
                myprinter.print_cyan(f"{item.name} removed from super directory")
ImageConverter(f"{tikpath.super}/super.img").lz4_compress(need_remove_old=True)

# 3. 打包
prepare.archive(ZIP_NAME)
