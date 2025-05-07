from pydantic import BaseModel

from server_schema import Server
from service_schema import Service, Istio


class Package(BaseModel):
    servicePackageName: str
    servicePackageDescription: str
    servicePackageType = "helm"
    servicePackageVersion: str
    serviceApplicationVersion: str
    serviceWorkLoad: str
    k8sService: str
    serviceMesh = "istio"
    gatewayStatus: str
    destinationRuleStatus: str
    virtualServiceStatus: str
    faultInjectionStatus: str
    serviceEntryStatus: str


class PackageResponse(BaseModel):
    service: list[Service]
    istio: Istio
    server: Server


class DeployPackage(BaseModel):
    service: list[Service] | None = None
    istio: Istio | None = None
    server: Server | None = None


class NetworkPackage(BaseModel):
    service: list[Service] | None = None
    istio: Istio | None = None


class ServerPackage(BaseModel):
    server: Server | None = None
