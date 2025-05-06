from src.custom import lp
from src.custom.ProductDealer import ProductDealer
from src.custom.SystemDealer import SystemDealer
from src.custom.VendorDealer import VendorDealer
from src.image.Image import MyImage
from src.image.ImagePacker import ImagePacker
from src.image.ImageUnpacker import ImageUnpacker
from tikpath import TikPath

tikpath = TikPath()
tikpath.set_project("UI7")


# ImageUnpacker("system").unpack()
# SystemDealer().perform_slim("chn")
ImagePacker("system").pack_ext().out2super()