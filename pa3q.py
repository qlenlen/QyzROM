"""
Samsung S25 Ultra 一键生成 QyzROM
国行
"""

from src.custom.ProductDealer import ProductDealer
from src.custom.SystemDealer import SystemDealer
from src.device import general
from src.image.Image import MyImage
from src.image.ImagePacker import ImagePacker
from src.image.ImageUnpacker import ImageUnpacker
from tikpath import TikPath
from src.custom import prepare, lp

from src.util.utils import MyPrinter

tikpath = TikPath()
tikpath.set_project("pa3q")

myprinter = MyPrinter()

DEVICE = "dm3q"
WORK = tikpath.project_path
PRIV_RESOURCE = tikpath.res_path_for(DEVICE)

ZIP_NAME = "S9380.zip"

general.clean()

# 1. 提取需要的文件
prepare.unarchive()

# 2.1 avb去除
general.deal_with_avb()

# 处理super
general.moveimg2project("AP", "super")
ImageUnpacker("super").unpack()
qti_size = lp.get_qti_dynamic_partitions_size()
device_size = lp.get_device_size()

ImageUnpacker("system_a").unpack()
SystemDealer("system_a", "pa3q").perform_slim("tgy")
ImagePacker("system_a").pack_ext().out2super()

ImageUnpacker("product_a").unpack()
ProductDealer("product_a", "pa3q").perform_slim("tgy")
ImagePacker("product_a").pack_ext().out2super()

MyImage("vendor_a").move2super()
MyImage("system_ext_a").move2super()
MyImage("odm_a").move2super()
MyImage("system_dlkm_a").move2super()
MyImage("vendor_dlkm_a").move2super()

sh = lp.make_sh(tikpath.super, device_size, qti_size, lp.SuperType.VAB)
lp.cook(sh, tikpath.super)

# 3. 打包
prepare.archive(ZIP_NAME)
