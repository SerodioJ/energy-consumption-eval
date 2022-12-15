import os
import argparse
import random
from tqdm import tqdm
from time import sleep
import requests
from pathlib import Path



def extract_args(args):
    nodes = args.placement.split(";")
    if len(nodes) == 1 and args.config != "local":
        raise ValueError("Invalid Value for Placement")
    
    seed = args.seed
    return nodes, args.config, seed, args.output




def evaluate(args):
    nodes, config, seed, output = extract_args(args)
    random.seed(seed)
    server = f"http://{nodes[0].split(':')[1]}:8080"
    for i in range(10):
        values = 2**i
        print(f"Add {values} values to list")
        for _ in tqdm(range(values)):
            requests.post(f"{server}/add", data=str(random.randint(1, 1000)))
        print(f"Get values from list - Iteration {i}")
        for _ in tqdm(range(10 if config == "propagate" else 5)):
            requests.get(f"{server}/get")
        
    for i, node in enumerate(nodes):
        node_name, ip = node.split(":") 
        base_url = f"http://{ip}:8000"
        regions = requests.get(f"{base_url}/export/regions")
        power = requests.get(f"{base_url}/export/power")

        with open(os.path.join(output, f"{config}_{i}_{node_name}_power.csv"), "w") as f:
            f.write(power.text)

        with open(os.path.join(output, f"{config}_{i}_{node_name}_regions.csv"), "w") as f:
            f.write(regions.text)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o", "--output", help="path to CSV outputs", type=Path, default="outputs_server"
    )

    parser.add_argument(
        "-c",
        "--config",
        help="proxy config to use",
        type=str,
        choices=["propagate", "sharding", "local"],
    )

    parser.add_argument(
        "-s",
        "--seed",
        help="seed for random number generator",
        type=int,
        default=10
    )


    parser.add_argument(
        "-p",
        "--placement",
        help="String containing info about node and their respective IPs, in the following order SERVER:IP;REMOTE_DIST:IP;REMOTE_DIST2:IP",
        required=True,
    )

    args = parser.parse_args()

    evaluate(args)
