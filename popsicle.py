"""
Xiaomi 17 Pro Max 一键生成 QyzROM
国行
"""

import os
import pathlib
import shutil

RUN_EXTRA_STEPS = os.getenv("RUN_EXTRA_STEPS") == "1"

from src.custom.ModuleDealer import ModuleDealer
from src.custom.VendorDealer import VendorDealer
from src.device import general
from src.image.Image import MyImage
from src.image.ImageConverter import ImageConverter
from tikpath import TikPath
from src.custom import prepare, lp
from src.util.utils import MyPrinter

tikpath = TikPath()
tikpath.set_project("TEST")

myprinter = MyPrinter()

DEVICE = "popsicle"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

general.clean()

# 1. 提取需要的文件
tgz_file_path = prepare.unarchive()
if RUN_EXTRA_STEPS:
    os.remove(tgz_file_path)

# 2. 分门别类处理镜像
# 2.1 avb去除
general.deal_with_avb()

# 2.2 内核替换
# now it's 5.15.195 lkm
# general.replace_kernel(PRIV_RESOURCE, WORK)
# 补充 进行ksu-lkm修补
general.patch_lkm("android16-6.12")

# 2.3 替换twrp
# general.replace_rec(PRIV_RESOURCE)

# 2.4 处理vendor_boot
general.deal_with_vboot(False)

# 2.5 处理optics
pass

# 处理super
general.moveimg2project("super")
MyImage("super").unpack()
qti_size = lp.get_qti_dynamic_partitions_size()
device_size = lp.get_device_size()
MyImage("super").unlink()

# unpack
img_vendor = MyImage("vendor_a")
img_vendor.unpack()

img_system = MyImage("system_a")
img_system.unpack()

img_mi_ext = MyImage("mi_ext_a")
img_mi_ext.unpack()

img_product = MyImage("product_a")
img_product.unpack()

img_system_ext = MyImage("system_ext_a")
img_system_ext.unpack()


VendorDealer().remove_avb()

# split mi_ext and move stuff to corresponding partition
ModuleDealer("MiExt").perform_task()

ModuleDealer("FixNfc").perform_task()

ModuleDealer("FixRecorder").perform_task()

# add binary to system
ModuleDealer("Binary").perform_task()

# preload apks
ModuleDealer("Preload").perform_task()

ModuleDealer("DeBloat").perform_task()

# repack and move to super
img_vendor.pack_erofs().out2super()
img_vendor.unlink().rm_content()

img_mi_ext.pack_ext().out2super()
img_product.pack_ext().out2super()
img_system.pack_ext().out2super()
img_system_ext.pack_ext().out2super()

if RUN_EXTRA_STEPS:
    img_system.unlink().rm_content()
    img_product.unlink().rm_content()
    img_mi_ext.unlink().rm_content()
    img_system_ext.unlink().rm_content()

# untouched partitions
MyImage("odm_a").move2super()
MyImage("system_dlkm_a").move2super()
MyImage("vendor_dlkm_a").move2super()

sh = lp.make_sh(tikpath.super, device_size, qti_size)
lp.cook(sh, tikpath.super)

# 清理super目录 只保留super.img
if RUN_EXTRA_STEPS:
    for item in pathlib.Path(tikpath.super).iterdir():
        if not item.name.startswith("super"):
            if not item.is_dir():
                item.unlink()
                myprinter.print_cyan(f"{item.name} removed from super directory")
ImageConverter(f"{tikpath.super}/super.img").zstd_compress(need_remove_old=True)

# 3. 打包
prepare.archive(__name__)
