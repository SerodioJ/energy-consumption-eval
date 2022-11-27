
import os
import numpy as np
import requests
from time import sleep

def fft():
    size = int(os.getenv("DIM_SIZE", 1e7))
    start = requests.post(f"{base_url}/region/start",json={"region": "data_init"})
    a = np.random.rand(size)*100
    end = requests.post(f"{base_url}/region/end",json=start.json())
    results = end.json()
    print(f"FFT - DATA_INIT: {results['energy']} J, {results['time']} s")

    start = requests.post(f"{base_url}/region/start",json={"region": "computation"})
    c = np.fft.fft(a)
    end = requests.post(f"{base_url}/region/end",json=start.json())
    results = end.json()
    print(f"FFT - COMPUTATION: {results['energy']} J, {results['time']} s")

def matmul():
    size = int(os.getenv("DIM_SIZE", 1e3))
    start = requests.post(f"{base_url}/region/start",json={"region": "data_init"})
    a = np.random.rand(size,size)*100
    b = np.random.rand(size,size)*100
    end = requests.post(f"{base_url}/region/end",json=start.json())
    results = end.json()
    print(f"MATMUL - DATA_INIT: {results['energy']} J, {results['time']} s")

    start = requests.post(f"{base_url}/region/start",json={"region": "computation"})
    c = np.matmul(a, b)
    end = requests.post(f"{base_url}/region/end",json=start.json())
    results = end.json()
    print(f"MATMUL - COMPUTATION: {results['energy']} J, {results['time']} s")

base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
while True:
    sleep(10)
    app = os.getenv("PYTHON_COMP", "matmul")
    if app == "matmul":
        matmul()
    elif app == "fft":
        fft()