import os
import sys

sys.path.append("/deploy/openapi")

import yaml
import json
from jsonmerge import merge
from shell import shell
import global_variables as gm
from coudtool_schema import DeployParams

from deploy_schema import DeployComponent, DeployLabel
from package_schema import Package, DeployPackage, NetworkPackage, ServerPackage
from fastapi import HTTPException
import random


def gen_service_with_package(package: Package):
    work_dir = gm.get_value("work_dir")
    json_file = work_dir + "/openapi/" + package.servicePackageName + '.ini'
    package_ini = ""
    json_data = package.dict()
    for i in json_data:
        package_ini = package_ini + i + "=\"" + json_data[i] + '\"' + '\n'

    with open(json_file, 'w+') as package_ini_file:
        package_ini_file.write(package_ini)
    cmd = "bash -x " + work_dir + "/service/serviceGenerator.sh" + " -f " + json_file
    print(cmd)
    output = shell(cmd)
    print(output.output())

    # return output.code
    server_json = gen_server_response_package(package)
    service_json = gen_service_response_package(package)
    result_json = merge(server_json, service_json)
    return result_json


def gen_server_response_package(package: Package):
    work_dir = gm.get_value("work_dir")
    ops_server = work_dir + "/service/output/data/" + package.servicePackageName + "-app" + package.serviceApplicationVersion + "/userValues.yaml"
    dev_server = work_dir + "/service/output/data/" + package.servicePackageName + "-app" + package.serviceApplicationVersion + "/devValues.yaml"
    with open(ops_server, 'r') as f:
        ops_server_json = yaml.safe_load(f)
    with open(dev_server, 'r') as f:
        dev_server_json = yaml.safe_load(f)

    server_json = merge(dev_server_json, ops_server_json)

    return server_json


def gen_service_response_package(package: Package):
    work_dir = gm.get_value("work_dir")
    ops_network = work_dir + "/service/output/data/" + package.servicePackageName + "-network" + "/userValues.yaml"
    with open(ops_network, 'r') as f:
        ops_network_json = yaml.safe_load(f)
    return ops_network_json


# ls = shell('bash -x ../service/serviceGenerator.sh  -f ../service/example/bookinfo/input/rating.ini')
# print(ls.output())


def deploy_helm_package(lab_name: str, helm_name: str, service_name: str, server_name: str):
    item = DeployParams(params={})
    item.workflow = "logic/mop/service/deployHelmPackage.md"

    item.params["LAB_NAME"] = lab_name
    item.params["HELM_PACKAGE"] = helm_name
    item.params["SERVICE_NAME"] = service_name
    item.params["DOMAIN_NAME"] = "default"
    invoke_cloud_tool_cmd(item)


def deploy_label(lab_name: str, deploy: DeployComponent):
    item = DeployParams(params={})
    item.workflow = "logic/mop/deploy/deployLabel.md"

    item.params["LAB_NAME"] = lab_name

    node_label: DeployLabel
    for node_label in deploy.label:
        item.params["NODES"] = " ".join(node_label.nodes)
        item.params["KEY"] = node_label.key
        item.params["VALUE"] = node_label.value
        invoke_cloud_tool_cmd(item)


def update_cluster_cmd(lab_name: str):
    item = DeployParams(params={})
    item.workflow = "logic/cloudFactory/setupK8s.md"

    item.params["LAB_NAME"] = lab_name
    invoke_cloud_tool_cmd(item)


def invoke_cloud_tool_cmd(item: DeployParams):
    work_dir = gm.get_value("work_dir")
    command = item.COMMAND
    workflow = item.workflow
    params = item.params
    cli = gm.get_value("cli")
    params_str = ""

    num = random.random()
    param_json = "{0}/output/{1}.json".format(work_dir, num)
    with open(param_json, 'w+') as f:
        json.dump(params, f, indent=3)

    for key, value in params.items():
        param = "{0}=\'{1}\'".format(key, value).replace(' ', '~').replace("&", "\&")
        params_str = params_str + " " + param

    cmd = "{4} -p 'COMMAND={1}' -a '{0}/{2}' -o \"{3}\"  -j {5} " \
        .format(work_dir, command, workflow, params_str, cli, param_json)

    print(cmd)
    result = shell(cmd)
    result_output_str = '\n'.join(result.output())  # Convert the list to a string
    print(result_output_str)
    work_dir = gm.get_value("work_dir")
    with open(work_dir + "/output/detail.logs", 'w+') as f:
        f.write(result_output_str)
    if result.code != 0:
        raise HTTPException(status_code=500, detail="command [[{}]] executed failed".format(cmd))


def deploy_paas_cmd(lab_name: str, deploy: DeployComponent):
    item = DeployParams(params={})
    item.workflow = "logic/mop/paas/{}.md".format(deploy.component_name)
    item.params["LAB_NAME"] = lab_name

    invoke_cloud_tool_cmd(item)


def gen_server_package_yaml(server_object: ServerPackage):
    if server_object is not None:
        work_dir = gm.get_value("work_dir")
        ops_server_path = work_dir + "/service/output/data/" + server_object.server.name + "-app" + server_object.server.version
        is_exist = os.path.exists(ops_server_path)
        if not is_exist:
            os.mkdir(ops_server_path)
        with open(ops_server_path + "/values.yaml", 'w+') as f:
            f.write(yaml.dump(server_object.dict()))


def gen_network_package_yaml(package_name: str, service_mesh_object: NetworkPackage):
    if service_mesh_object is not None:
        work_dir = gm.get_value("work_dir")
        ops_service_mesh_path = work_dir + "/service/output/data/" + package_name + "-network"
        is_exist = os.path.exists(ops_service_mesh_path)
        if not is_exist:
            os.mkdir(ops_service_mesh_path)
        with open(ops_service_mesh_path + "/values.yaml", 'w+') as f:
            f.write(yaml.dump(service_mesh_object.dict()))


def deploy_server_package_cmd(lab_name: str, server_package: ServerPackage):
    package_name = server_package.server.name
    gen_server_package_yaml(server_package)

    # helm_app_name
    helm_app_name = server_package.server.name + "-app" + server_package.server.version
    helm_app_package = server_package.server.name + "-app"
    deploy_helm_package(lab_name, helm_app_package, helm_app_name, server_package.server.name)


def deploy_network_package_cmd(lab_name: str, package_name: str, network_package: NetworkPackage):
    gen_network_package_yaml(package_name, network_package)

    # helm_network_name
    helm_network_name = package_name + "-network"
    deploy_helm_package(lab_name, helm_network_name, helm_network_name, package_name)


def deploy_package_cmd(lab_name: str, package: DeployPackage):
    package_name = package.server.name
    server_package = ServerPackage()
    server_package.server = package.server
    network_package = NetworkPackage()
    network_package.istio = package.istio
    network_package.service = package.service

    deploy_server_package_cmd(lab_name, server_package)
    deploy_network_package_cmd(lab_name, package_name, network_package)


def get_network_cmd(network_name: str):
    work_dir = gm.get_value("work_dir")
    ops_network_yaml = work_dir + "/service/output/data/" + network_name + "/values.yaml"
    with open(ops_network_yaml, 'r') as f:
        ops_network_json = yaml.safe_load(f)
    return ops_network_json


def get_server_cmd(server_name: str):
    work_dir = gm.get_value("work_dir")
    ops_network_yaml = work_dir + "/service/output/data/" + server_name + "/values.yaml"
    with open(ops_network_yaml, 'r') as f:
        ops_network_json = yaml.safe_load(f)
    return ops_network_json
