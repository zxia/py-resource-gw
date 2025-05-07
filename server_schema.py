from pydantic import BaseModel


class Image(BaseModel):
    repository: str
    tag: str
    pullPolicy: str
    imagePullSecrets: str


class Env(BaseModel):
    name: str
    value: str


class Volume(BaseModel):
    name: str
    emptyDir: dict | None = None


class VolumeMount(BaseModel):
    name: str
    mountPath: str


class Command(BaseModel):
    command: list[str]


class Probe(BaseModel):
    exec: Command
    failureThreshold: int
    initialDelaySeconds: int
    periodSeconds: int
    timeoutSeconds: int


class Resource(BaseModel):
    memory: str
    cpu: str


class Resources(BaseModel):
    requests: Resource | None = None
    limits: Resource | None = None


class Server(BaseModel):
    image: Image
    name: str | None = None
    replica: int
    version: str
    env: list[Env] | None = None
    extraContainerargs: dict | None = None
    volumeMounts: list[VolumeMount] | None = None
    volumes: list[Volume] | None = None
    command: str | None = None
    args: list[str] | None = None
    readinessProbe: Probe | None = None
    livenessProbe: Probe | None = None
    resources: Resources | None = None


class DeployServer(BaseModel):
    server: Server
