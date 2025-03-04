import pathlib
from typing import Literal

import os
import shutil

from src.custom.CscEditor import CscEditor
from src.custom.Vbmeta import Vbmeta
from src.image.ImageConverter import ImageConverter
from src.image.ImagePacker import ImagePacker
from src.image.ImageUnpacker import ImageUnpacker
from src.image.VendorBoot import VendorBoot
from src.image.image import Kernel, BootImg
from src.util.utils import MyPrinter
from tikpath import TikPath

tikpath = TikPath()
myprinter = MyPrinter()


def moveimg2project(folder: Literal["AP", "BL", "CSC"], img_name: str) -> str:
    """Move from extract folder to project root
    Return the dest path of the image"""
    src = f"{tikpath.project_path}/{folder}/{img_name}.img"
    dest = f"{tikpath.project_path}/{img_name}.img"
    if os.path.exists(dest):
        os.remove(dest)
    shutil.move(src, dest)
    return f"{tikpath.project_path}/{img_name}.img"


def deal_with_avb():
    """Move vbmeta and vbmeta_system to project root
    Deal with them and move them to out folder"""
    moveimg2project("BL", "vbmeta")
    Vbmeta("vbmeta").deal_with().move2out()
    moveimg2project("AP", "vbmeta_system")
    Vbmeta("vbmeta_system").deal_with().move2out()


def replace_rec(private_resource: str):
    """Replace twrp recovery.img"""
    if os.path.exists(rec := f"{private_resource}/twrp/recovery.img"):
        shutil.copyfile(rec, tikpath.img_output_path("recovery"))
    else:
        myprinter.print_red("No twrp recovery.img found")


def deal_with_vendor():
    """Move vendor_boot.img to project root
    Deal with it and move it to out folder"""
    moveimg2project("AP", "vendor_boot")
    VendorBoot().deal_with()


def deal_with_optics():
    """Move optics.img to project root
    Unpack it"""
    moveimg2project("CSC", "optics")
    ImageUnpacker("optics").unpack()
    optics_inner = "configs/carriers/TGY/conf/system/cscfeature.xml"
    fp = os.path.join(tikpath.get_content_path("optics"), optics_inner)
    CscEditor(fp).perform_tgy()
    ImagePacker("optics").pack("ext")
    ImageConverter(tikpath.img_output_path("optics")).img2simg()


def replace_kernel(private_resource: str, work: str):
    resource_kernel = Kernel(f"{private_resource}/kernel/kernel")
    if not resource_kernel.exists():
        myprinter.print_red("No kernel found")
        return
    myprinter.print_white(resource_kernel.read_version())

    with BootImg(f"{work}/AP/boot.img") as origin_boot:
        # 此块内工作目录为 {WORK}/AP
        origin_boot.unpack()
        os.system(f"rm kernel")
        resource_kernel.copy_to(f"{work}/AP/kernel")
        origin_boot.repack()
        origin_boot.move2out()


def clean():
    """Clean the project folder"""
    for x in pathlib.Path(tikpath.project_path).iterdir():
        if x.is_dir():
            if x.name == "config" or x.name == "TI_out":
                continue
            shutil.rmtree(x)
        else:
            if not x.suffix == ".zip":
                x.unlink()
