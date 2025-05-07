from pydantic import BaseModel


class DeployParams(BaseModel):
    COMMAND = "deploy"
    workflow = "/logic/mop/service/deployHelmPackage.md"
    params: dict
