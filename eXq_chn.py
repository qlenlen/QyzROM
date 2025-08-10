"""
Samsung S24 Series 一键生成 QyzROM
国行
"""

import os
import pathlib
import shutil

RUN_EXTRA_STEPS = os.getenv("RUN_EXTRA_STEPS") == "1"

from src.custom.CscEditor import CscEditor, get_csc_fp, get_ff_fp
from src.custom.ModuleDealer import ModuleDealer
from src.custom.ProductDealer import ProductDealer
from src.custom.SystemDealer import SystemDealer
from src.custom.VendorDealer import VendorDealer
from src.custom.XmlEditor import FFEditor
from src.device import general
from src.image.Image import MyImage
from src.image.ImageConverter import ImageConverter
from tikpath import TikPath
from src.custom import prepare, lp

from src.util.utils import MyPrinter

tikpath = TikPath()
tikpath.set_project("UI7")

myprinter = MyPrinter()

DEVICE = "e3q"
AREA = "chn"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

ZIP_NAME = "S9280.zip"

general.clean()

# 1. 提取需要的文件
prepare.unarchive(skip_zip=False, remove_tars=RUN_EXTRA_STEPS)

# 2. 分门别类处理镜像
# 2.1 avb去除
general.deal_with_avb()

# 2.2 内核替换
# now it's 6.1 BKLYN GKI
general.replace_kernel(PRIV_RESOURCE, WORK)

# 2.3 替换twrp
# general.replace_rec(PRIV_RESOURCE)

# 2.4 处理vendor_boot
general.deal_with_vboot()

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

img_vendor = MyImage("vendor")
img_vendor.unpack()
VendorDealer().perform_slim()
img_vendor.pack_erofs().out2super()
if RUN_EXTRA_STEPS:
    img_vendor.unlink().rm_content()

img_system = MyImage("system")
img_system.unpack()
SystemDealer(version="V1.1").perform_slim("chn")
ModuleDealer("Media").perform_task()
ModuleDealer("Binary").perform_task()
ModuleDealer("Fonts_V2").perform_task()
ModuleDealer("OneDesign").perform_task()
ModuleDealer("Preload").perform_task()
ModuleDealer("TgyStuff").perform_task()
ModuleDealer("BriefSupport").perform_task()

FFEditor.from_toml(
    get_ff_fp(),
    f"{tikpath.res_path}/{DEVICE}/tasks/{AREA}/ff.toml",
).save_xml()
img_system.pack_ext().out2super()

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

MyImage("odm").move2super()
MyImage("system_dlkm").move2super()

img_vendor_dlkm = MyImage("vendor_dlkm").unpack()
ModuleDealer("BatteryKO_24").perform_task()
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
                myprinter.print_cyan(f"{item.name} removed from super directory")
ImageConverter(f"{tikpath.super}/super.img").lz4_compress(need_remove_old=True)

# 3. 打包
prepare.archive(ZIP_NAME, need_remove_img=RUN_EXTRA_STEPS)
