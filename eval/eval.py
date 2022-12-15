import os
import argparse
import yaml
from time import sleep
import requests
from pathlib import Path

from kubernetes import client, config
from kubernetes.client.rest import ApiException

exp_config = {
    "dana-matmul": {
        "image": "serodioj/ecs-proxy:dana",
        "name": "DANA_COMP",
        "value": "MatMul",
    },
    "dana-default": {
        "image": "serodioj/ecs-proxy:dana",
        "name": "DANA_COMP",
        "value": "MatMul_Default",
    },
    "python-matmul": {
        "image": "serodioj/ecs-proxy:python",
        "name": "PYTHON_COMP",
        "value": "matmul",
    },
    "python-fft": {
        "image": "serodioj/ecs-proxy:python",
        "name": "PYTHON_COMP",
        "value": "fft",
    }
}

def extract_args(args):
    if args.use_all:
        config = ["dana-matmul", "dana-default", "python-matmul", "python-fft"]
    else:
        config = args.config
    ip_port = f"{args.service_ip}:8000"
    with open(f"kubernetes/{args.placement}.yaml", "r") as f:
        deployment = yaml.safe_load(f)
    return config, ip_port, args.placement, deployment, args.output, args.samples



def delete_deployment(deployment):
    config.load_kube_config()
    v1 = client.AppsV1Api()
    try:
        v1.delete_namespaced_deployment(
            name=deployment["metadata"]["name"], namespace="default"
        )
    except ApiException as e:
        pass
    return

def update_deployment(deployment, conf):
    config.load_kube_config()
    v1 = client.AppsV1Api()
    try:
        v1.delete_namespaced_deployment(
            name=deployment["metadata"]["name"], namespace="default"
        )
    except ApiException as e:
        pass
    deployment["spec"]["template"]["spec"]["containers"][1]["image"] = exp_config[conf]["image"]
    deployment["spec"]["template"]["spec"]["containers"][1]["env"][0]["name"] = exp_config[conf]["name"]
    deployment["spec"]["template"]["spec"]["containers"][1]["env"][0]["value"] = exp_config[conf]["value"]
    v1.create_namespaced_deployment(namespace="default", body=deployment)
    return

def check_samples(ip_port, samples):
    req = requests.get(f"http://{ip_port}/export/regions")
    curr = len(req.text.split("computation")) - 1
    print(f"{curr}/{samples} samples acquired")
    return curr < samples


def evaluate(args):
    config_list, ip_port, placement, deployment, output, samples = extract_args(args)
    for config in  config_list:
        print(f"Executing Experiment for {config}")
        update_deployment(deployment, config)
        sleep(120)
        while (check_samples(ip_port, samples)):
            sleep(60)

        regions = requests.get(f"http://{ip_port}/export/regions")
        power = requests.get(f"http://{ip_port}/export/power")

        with open(os.path.join(output, f"{placement}_{config}_power.csv"), "w") as f:
            f.write(power.text)

        with open(os.path.join(output, f"{placement}_{config}_regions.csv"), "w") as f:
            f.write(regions.text)
    delete_deployment(deployment)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o", "--output", help="path to CSV outputs", type=Path, default="outputs"
    )

    parser.add_argument(
        "-s", "--service-ip", help="Service IP address", type=str, required=True
    )

    parser.add_argument(
        "-c",
        "--config",
        help="proxy config to use",
        nargs="+",
        type=str,
        choices=["dana-matmul", "dana-default", "python-matmul", "python-fft"],
    )

    parser.add_argument(
        "-n",
        "--samples",
        help="number of samples",
        type=int,
        default=10,
    )

    parser.add_argument(
        "-a",
        "--all",
        help="use all proxy configurations",
        dest="use_all",
        action="store_true",
    )

    parser.add_argument(
        "-p",
        "--placement",
        help="where to place service",
        choices=["rasp3", "rasp4", "xps", "g3"],
        default="rasp4",
    )

    args = parser.parse_args()

    evaluate(args)
