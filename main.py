import os

import uvicorn
from fastapi import FastAPI
from fastapi import applications
from fastapi.openapi.docs import get_swagger_ui_html

from cluster_schema import ClusterInfo
from base_schema import BaseInfo
from coudtool_schema import DeployParams
from deploy_schema import Deploy, DeployComponent
from k8s_schema import K8sInfo
from paas_schema import PaasInfo
from package_schema import Package, PackageResponse, DeployPackage, ServerPackage, NetworkPackage
from shellcmd import gen_service_with_package, deploy_package_cmd, deploy_server_package_cmd, \
    deploy_network_package_cmd, get_server_cmd, get_network_cmd, deploy_paas_cmd, update_cluster_cmd, \
    invoke_cloud_tool_cmd, deploy_label
from utility import gen_cluster_ini, get_cluster_configure, gen_paas_ini, gen_k8s_ini, gen_paas_label, \
    get_k8s_configure, get_paas_configure, gen_base_ini, get_base_configure

app = FastAPI()
workDir: str


@app.post("/deploy/server")
def deploy_server(lab_name: str, item: ServerPackage, deploy: DeployComponent):
    deploy_label(lab_name, deploy)
    deploy_server_package_cmd(lab_name, item)
    return item


@app.post("/deploy/servicemesh/servicename")
def deploy_service(service_name: str, lab_name: str, item: NetworkPackage):
    deploy_network_package_cmd(lab_name, service_name, item)
    return item


@app.post("/package/create/", response_model=PackageResponse)
def create_package(item: Package):
    result = gen_service_with_package(item)
    return result


@app.post("/package/deploy/")
def deploy_package(lab_name: str, item: DeployPackage, deploy: DeployComponent):
    deploy_label(lab_name, deploy)
    deploy_package_cmd(lab_name, item)
    return item


@app.get("/server/name", response_model=ServerPackage)
def get_server(name: str):
    json_result = get_server_cmd(name)
    return json_result


@app.get("/network/name", response_model=NetworkPackage)
def get_service(name: str):
    json_result = get_network_cmd(name)
    return json_result


@app.put("/cluster/config")
def update_cluster_config(lab_name: str, item: ClusterInfo):
    gen_cluster_ini(lab_name, item)
    return item


@app.get("/cluster/config/lab_name", response_model=ClusterInfo)
def get_cluster_config(lab_name: str):
    cluster_config = get_cluster_configure(lab_name)
    return cluster_config


@app.post("/cluster/update/lab_name")
def update_cluster(lab_name: str):
    update_cluster_cmd(lab_name)


@app.post("/paas/config/lab_name")
def update_paas_config(lab_name: str, item: PaasInfo):
    gen_paas_ini(lab_name, item)
    return item


@app.get("/paas/config/lab_name", response_model=PaasInfo)
def get_paas_config(lab_name: str):
    k8s_config = get_paas_configure(lab_name)
    return k8s_config


@app.post("/paas/deploy")
def deploy_paas(deploy: Deploy, item: PaasInfo | None = None):
    lab_name = deploy.lab
    if item is not None:
        gen_paas_ini(lab_name, item)
    gen_paas_label(deploy)

    deploy_component: DeployComponent
    for deploy_component in deploy.component:
        deploy_paas_cmd(deploy.lab, deploy_component)


@app.post("/k8s/config/lab_name")
def update_k8s_config(lab_name: str, item: K8sInfo):
    gen_k8s_ini(lab_name, item)
    return item


@app.get("/k8s/config/lab_name", response_model=K8sInfo)
def get_k8s_config(lab_name: str):
    k8s_config = get_k8s_configure(lab_name)
    return k8s_config


@app.post("/base/config/")
def update_base_config(lab_name: str, item: BaseInfo):
    gen_base_ini(lab_name, item)
    return item


@app.get("/k8s/config/lab_name", response_model=BaseInfo)
def get_base_config(lab_name: str):
    base_config = get_base_configure(lab_name)
    return base_config


@app.post("/build/saverpm/")
def build_rpms(lab_name: str, host_ip: str):
    item = DeployParams(params={})
    item.workflow = "logic/mop/build/saveRpmPackage.md"
    item.COMMAND = "build"

    item.params["SSH_HOST"] = host_ip
    item.params["LAB_NAME"] = lab_name
    res = invoke_cloud_tool_cmd(item)
    return res


@app.put("/command/cloud")
def exec_cloud_command(item: DeployParams):
    res = invoke_cloud_tool_cmd(item)
    return res


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url='https://cdn.bootcdn.net/ajax/libs/swagger-ui/4.10.3/swagger-ui-bundle.js',
        swagger_css_url='https://cdn.bootcdn.net/ajax/libs/swagger-ui/4.10.3/swagger-ui.css'
    )


applications.get_swagger_ui_html = swagger_monkey_patch


def init():
    import global_variables as gm
    gm._init_()
    work_dir = os.getenv("work_dir")
    gm.set_value("work_dir", work_dir)
    command = os.getenv("cli")
    gm.set_value("cli", command)


if __name__ == "__main__":
    init()

    uvicorn.run(app, host="0.0.0.0", port=8000)
