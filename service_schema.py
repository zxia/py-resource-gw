##define the K8s service for the workload
from pydantic import BaseModel


class Protocol(BaseModel):
    protocol: str
    appProtocol: str
    port: str
    targetPort: str


class Service(BaseModel):
    name: str
    protocols: list[Protocol]


class Port(BaseModel):
    number: str
    name: str
    protocol: str


class Server(BaseModel):
    port: Port
    hosts: list[str]


class Gateway(BaseModel):
    name: str
    selector: str
    servers: list[Server]


class VirtualService(BaseModel):
    name: str
    hosts: list[str] | None = None
    gateways: list[str] | None = None
    http: list | None = None


class DestinationRule(BaseModel):
    name: str
    host: str
    subsets: list


class Istio(BaseModel):
    deployed: bool
    gateway: list[Gateway] | None = None
    virtualservice: list[VirtualService] | None = None
    destination: DestinationRule | None = None


class ServiceMesh(BaseModel):
    service: list[Service]
    istio: Istio

