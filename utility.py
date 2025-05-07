#!/usr/bin/env python
import json
import os
import sys

sys.path.append("/deploy/openapi")
import yaml
from jsonmerge import merge

import global_variables as gm
from cluster_schema import ClusterInfo
from base_schema import BaseInfo
from deploy_schema import Deploy, DeployComponent, DeployLabel
from k8s_schema import K8sInfo
from paas_schema import PaasInfo
from server_schema import DeployServer


def convert_json_to_yaml(json_file: str, yaml_file: str):
    with open(json_file, 'r') as f:
        json_data = json.loads(f.read())

    with open(yaml_file, 'w+') as f:
        f.write(yaml.dump(json_data))


def save_json_to_yaml(json_data: DeployServer, yaml_file: str):
    with open(yaml_file + '.json', 'w+') as f:
        json.dump(json_data.dict(), f, indent=3)
    convert_json_to_yaml(yaml_file + '.json', yaml_file + '.yaml')


#    with open(yaml_file+".yaml", 'w+') as f:
#       f.write(yaml.dump(json_data.json()))


def convert_yaml_to_json(yaml_file: str, json_file: str):
    with open(yaml_file, 'r') as f:
        yaml_data = yaml.safe_load(f)

    with open(json_file, 'w+') as f:
        json.dump(yaml_data, f, indent=3)


def gen_paas_label(deploy: Deploy):
    work_dir = gm.get_value("work_dir")
    lab_path = work_dir + "/lab/" + deploy.lab

    deploy_component: DeployComponent

    for deploy_component in deploy.component:
        node_label: DeployLabel
        for node_label in deploy_component.label:
            with open(lab_path + "/" + node_label.value + ".label", 'w+') as f:
                f.write(" ".join(node_label.nodes))


def get_cluster_configure(lab_name: str):
    return get_configure_common(lab_name, "cluster")


def get_k8s_configure(lab_name: str):
    return get_configure_common(lab_name, "k8s")


def get_paas_configure(lab_name: str):
    return get_configure_common(lab_name, "paas")


def get_base_configure(lab_name: str):
    return get_configure_common(lab_name, "base")


def get_configure_common(lab_name: str, component: str):
    work_dir = gm.get_value("work_dir")
    lab_path = work_dir + "/lab/" + lab_name
    with open(lab_path + "/" + component + ".json", 'r') as f:
        json_data = json.loads(f.read())
    return json_data


def get_lab_path(lab_name: str):
    work_dir = gm.get_value("work_dir")
    lab_path = work_dir + "/lab/" + lab_name
    return lab_path


def get_node_path(lab_name: str, node_name: str):
    work_dir = gm.get_value("work_dir")
    lab_path = "{0}/lab/{1}/{2}".format(work_dir, lab_name, node_name)
    return lab_path


def merge_json_and_save(new_json: dict, old_json_path: str):
    old_json: json
    merge_json = new_json
    is_file_exist = os.path.exists(old_json_path)
    if is_file_exist:
        with open(old_json_path, 'r') as f:
            old_json = json.loads(f.read())
            merge_json = merge(old_json, new_json)

    old_json_dir = os.path.dirname(old_json_path)
    is_exist = os.path.exists(old_json_dir)
    if not is_exist:
        os.makedirs(old_json_dir)

    with open(old_json_path, 'w+') as f:
        json.dump(merge_json, f, indent=3)

    return merge_json


def gen_config_common_ini(component: str, elements: dict):
    component_ini = "#Configuration Begin\n"
    key: str

    for key in elements:
        component_ini = component_ini + "{}_{}={}\n".format(component.upper(), key.upper(),
                                                            elements[key])
    component_ini = component_ini + "#Configuration End"

    return component_ini


def gen_config_raw_ini(component: str, elements: dict):
    component_ini = "#Configuration Begin\n"
    key: str

    for key in elements:
        component_ini = component_ini + "{0}={1}\n".format(key, elements[key])
    component_ini = component_ini + "#Configuration End"

    return component_ini


def gen_node_config_ini(component: str, elements: dict):
    component_ini = "#Configuration Begin\n"
    node_info: dict
    for node in elements:
        node_info = node["info"]
        component_ini = component_ini + "{}\t{}\t{}\t{}\n" \
            .format(node_info["name"], node_info["type"], node_info["zone"], node_info["private_ip"])
    component_ini = component_ini + "#Configuration End"

    return component_ini


def gen_paas_ini(lab_name: str, paas_info: PaasInfo):
    lab_path = get_lab_path(lab_name)
    json_path = "{0}/{1}.json".format(lab_path, "paas")
    new_json = paas_info.dict(exclude_none=True)

    gen_common_ini(json_path, new_json)


def gen_base_ini(lab_name: str, base_info: BaseInfo):
    lab_path = get_lab_path(lab_name)
    json_path = "{0}/{1}.json".format(lab_path, "base")
    new_json = base_info.dict(exclude_none=True)

    gen_common_ini(json_path, new_json)


def gen_k8s_ini(lab_name: str, k8s_info: K8sInfo):
    lab_path = get_lab_path(lab_name)
    json_path = "{0}/{1}.json".format(lab_path, "k8s")

    new_json = k8s_info.dict(exclude_none=True)
    json_merge = merge_json_and_save(new_json, json_path)

    component: str
    for component in new_json.keys():
        if component == "k8s":
            component_ini = gen_config_raw_ini(component, json_merge[component])
        else:
            component_ini = gen_config_common_ini(component, json_merge[component])

        with open(lab_path + "/" + component + ".ini", 'w+') as f:
            f.write(component_ini)


def gen_cluster_ini(lab_name: str, cluster_info: ClusterInfo):
    lab_path = get_lab_path(lab_name)
    json_path = "{0}/{1}.json".format(lab_path, "cluster")

    new_json = cluster_info.dict(exclude_none=True)
    json_merge = merge_json_and_save(new_json, json_path)

    component: str
    for component in new_json.keys():
        if component == "nodes":
            component_ini = gen_node_config_ini(component, json_merge[component])
        else:
            component_ini = gen_config_common_ini(component, json_merge[component])

        with open(lab_path + "/" + component + ".ini", 'w+') as f:
            f.write(component_ini)

    gen_nodes_ini(lab_name, cluster_info)


def gen_common_ini(json_path: str, new_json: dict):
    json_merge = merge_json_and_save(new_json, json_path)
    json_dir = os.path.dirname(json_path)
    component: str
    for component in new_json.keys():
        component_ini = gen_config_common_ini(component, json_merge[component])
        with open(json_dir + "/" + component + ".ini", 'w+') as f:
            f.write(component_ini)


def gen_node_ini(lab_name: str, node_name: str, new_json: dict):
    lab_path = get_node_path(lab_name, node_name)
    json_path = "{0}/{1}.json".format(lab_path, "node")

    gen_common_ini(json_path, new_json)


def gen_nodes_ini(lab_name: str, cluster_info: ClusterInfo):
    if cluster_info.nodes is not None:
        for node in cluster_info.nodes:
            gen_node_ini(lab_name, node.info.name, node.dict(exclude_none=True))

# convert_yaml_to_json('testServiceMesh.yaml', 'testServiceMesh.json')
# convert_json_to_yaml('product1.json', 'userValues1.yaml')
