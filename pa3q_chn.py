"""
Samsung S25 Ultra 一键生成 QyzROM
国行
"""

import os

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
from src.image.ImagePacker import ImagePacker
from src.image.ImageUnpacker import ImageUnpacker
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
prepare.unarchive(skip_zip=True)

# 2. 分门别类处理镜像
# 2.1 avb去除
general.deal_with_avb()

# 2.2 内核替换
pass

# 2.3 替换twrp
pass

# 2.4 处理vendor_boot
general.deal_with_vboot()

# 2.5 处理optics
general.moveimg2project("CSC", "optics")
ImageUnpacker("optics").unpack()
CscEditor(get_csc_fp("CHC")).perform_chn()
ImagePacker("optics").pack("ext")
ImageConverter(tikpath.img_output_path("optics")).img2simg()

# 处理super
general.moveimg2project("AP", "super")
ImageUnpacker("super").unpack()
qti_size = lp.get_qti_dynamic_partitions_size()
device_size = lp.get_device_size()

ImageUnpacker("product_a").unpack()
ProductDealer("product_a", "pa3q").perform_slim("chn")
ImagePacker("product_a").pack_erofs().out2super()

ImageUnpacker("vendor_a").unpack()
VendorDealer(is_aonly=False).fill_mount_point()
ImagePacker("vendor_a").pack_erofs().out2super()

ImageUnpacker("system_a").unpack()
SystemDealer("system_a", "pa3q").perform_slim("chn")

ModuleDealer("Binary", is_vab=True).perform_task()
ModuleDealer("Fonts", is_vab=True).perform_task()
ModuleDealer("Preload", is_vab=True).perform_task()
ModuleDealer("OneDesign", is_vab=True).perform_task()
ModuleDealer("TgyStuff", is_vab=True).perform_task()

FFEditor.from_toml(get_ff_fp(), f"{tikpath.res_path}/{DEVICE}/tasks/{AREA}/ff.toml", ).save_xml()

ImagePacker("system_a").pack_ext().out2super()

MyImage("system_ext_a").move2super()
MyImage("odm_a").move2super()
MyImage("system_dlkm_a").move2super()
MyImage("vendor_dlkm_a").move2super()

sh = lp.make_sh(tikpath.super, device_size, qti_size, SuperType.VAB)
lp.cook(sh, tikpath.super)

# 3. 打包
prepare.archive(ZIP_NAME)
