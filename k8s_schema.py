from pydantic import BaseModel


class K8s(BaseModel):
    controlPlaneEndpoint = "apiservervip"
    podNetworkCidr: str
    kubernetesVersion = "v1.24.3"
    k8sCidr: str
    controlPlaneEndpointIP: str
    serviceCidr: str


class K8sInfo(BaseModel):
    k8s: K8s
