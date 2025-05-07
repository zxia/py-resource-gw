from pydantic import BaseModel


class DeployLabel(BaseModel):
    nodes: list[str]
    key: str
    value: str


class DeployComponent(BaseModel):
    label: list[DeployLabel]
    component_name: str | None = None


class Deploy(BaseModel):
    lab: str
    component: list[DeployComponent]
