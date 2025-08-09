import pathlib
from typing import Literal

import os
import shutil

from src.custom.BootPatch import BootPatch
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


def patch_lkm(
    kmi: Literal[
        "android12-5.10",
        "android13-5.10",
        "android13-5.15",
        "android14-5.15",
        "android14-6.1",
        "android15-6.6",
    ]
):
    """Patch lkm.img in AP folder"""
    moveimg2project("AP", "init_boot")
    BootPatch.patch(img_path=tikpath.img_path("init_boot"), kmi=kmi)
    # rename the patched image to init_boot.img
    for x in pathlib.Path(tikpath.output_path).iterdir():
        if x.is_file() and x.name.startswith("kernelsu_patched"):
            os.rename(x, tikpath.img_output_path("init_boot"))
            myprinter.print_green(f"Renamed {x.name} -> init_boot.img")


def replace_rec(private_resource: str):
    """Replace twrp recovery.img"""
    if os.path.exists(rec := f"{private_resource}/twrp/recovery.img"):
        shutil.copyfile(rec, tikpath.img_output_path("recovery"))
    else:
        myprinter.print_red("No twrp recovery.img found")


def deal_with_vboot(remove_encryption: bool = True):
    """Move vendor_boot.img to project root
    Deal with it and move it to out folder"""
    moveimg2project("AP", "vendor_boot")
    with VendorBoot() as vboot:
        vboot.unpack()
        vboot.remove_avb()
        if remove_encryption:
            vboot.remove_encryption()
        vboot.fill_mount_point()
        vboot.repack()


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
            if x.name == "config" or x.name == "TI_out" or x.name == "tars":
                continue
            shutil.rmtree(x)
        else:
            if not x.suffix == ".zip":
                x.unlink()
