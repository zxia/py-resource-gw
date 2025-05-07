from pydantic import BaseModel


class Argocd(BaseModel):
    uri: str
    user: str
    password: str


class ElasticSearch(BaseModel):
    master_volume: str
    data_volume: str
    master_replicas: str
    master_password: str
    data_replicas: str
    ingest_replicas: str
    kibana_user: str
    kibana_password: str


class FileBeat(BaseModel):
    container_path = "/largeDisk/containers"


class Grafana(BaseModel):
    anonymouse: str
    volume: str
    password: str


class Istio(BaseModel):
    gateway_type = "NodePort"


class Kafka(BaseModel):
    kafka_volume: str
    zookeeper_volume: str


class Kibana(BaseModel):
    replicas: str
    service_type = "NodePort"


class Logstash(BaseModel):
    replicas: str


class Mariadb(BaseModel):
    volume: str
    password: str


class Mongodb(BaseModel):
    sharded_shard_number: str
    sharded_data_volume: str
    sharded_config_volume: str
    sharded_password: str


class Nacos(BaseModel):
    replicas: str
    db_type: str
    db_host: str
    db_name: str
    db_username: str
    db_port: str
    db_password: str


class Prometheus(BaseModel):
    server_volume: str
    alert_manager_volume: str


class Redis(BaseModel):
    volume: str | None = None
    node_number: str | None = None
    password: str | None = None
    cluster_volume: str | None = None
    cluster_node_number: str | None = None
    cluster_password: str | None = None
    cluster_replica: str | None = None


class Seaweedfs(BaseModel):
    data_volume: str
    idx_volume: str
    master_port: str
    master_node_port: str
    filer_port: str
    filer_node_port: str
    master_replicas: str
    volume_replicas: str
    filer_replicas: str


class Topolvm(BaseModel):
    volume: str


class Volcano(BaseModel):
    name = "volcano"


class PaasInfo(BaseModel):
    argocd: Argocd | None = None
    elasticsearch: ElasticSearch | None = None
    filebeat: FileBeat | None = None
    grafana: dict | None = None
    istio: Istio | None = None
    kafka: Kafka | None = None
    kibana: Kibana | None = None
    logstash: Logstash | None = None
    mariadb: Mariadb | None = None
    mongodb: Mongodb | None = None
    nacos: Nacos | None = None
    prometheus: Prometheus | None = None
    redis: Redis | None = None
    seaweedfs: Seaweedfs | None = None
    topolvm: Topolvm | None = None
    volcano: Volcano | None = None
