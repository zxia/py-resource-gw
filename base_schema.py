from pydantic import BaseModel


class HarborBase(BaseModel):
    host_name = "gmct.storage.com"
    password = "Ctsi5G@2021"
    data_volume = "/largerDisk"
    data_password = "harborDb@2022"
    version = "v2.3.1"


class BaseInfo(BaseModel):
    harborbase: HarborBase
