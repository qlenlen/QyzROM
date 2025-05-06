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

general.clean()

# 1. 提取需要的文件
prepare.unarchive()

# 2. 分门别类处理镜像
# 2.1 avb去除
general.deal_with_avb()

# 2.2 内核替换
general.replace_kernel(PRIV_RESOURCE, WORK)

# 2.3 替换twrp
pass

# 2.4 处理vendor_boot
general.deal_with_vendor()

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

ImageUnpacker("vendor").unpack()
VendorDealer().perform_slim()
ImagePacker("vendor").pack_erofs().out2super()

ImageUnpacker("system").unpack()
SystemDealer(version="V2.1").perform_slim("chn")
ModuleDealer("Media").perform_task()
ModuleDealer("Binary").perform_task()
ModuleDealer("Fonts").perform_task()

FFEditor.from_toml(get_ff_fp(), f"{tikpath.res_path}/{DEVICE}/tasks/{AREA}/ff.toml", ).save_xml()

ImagePacker("system").pack_ext().out2super()

ImageUnpacker("product").unpack()
ProductDealer().perform_slim("chn")
ImagePacker("product").pack_erofs().out2super()

ImageUnpacker("system_ext").unpack()
ImagePacker("system_ext").pack_ext().out2super()

MyImage("odm").move2super()
MyImage("system_dlkm").move2super()
MyImage("vendor_dlkm").move2super()

sh = lp.make_sh(tikpath.super, device_size, qti_size)
lp.cook(sh, tikpath.super)

# 3. 打包
prepare.archive(ZIP_NAME)
