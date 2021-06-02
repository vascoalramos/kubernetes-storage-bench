import subprocess
import json
import sys
from time import sleep, time
from datetime import datetime
import os
import psutil

# Terminate process and its children
def terminate(procPid):
    process = psutil.Process(procPid)
    for proc in process.children(recursive=True):
        proc.terminate()
    process.terminate()

# Environment configuration
CLUSTER_MACHINES = ["cloud74", "cloud75", "cloud76"]
STORAGE_MACHINES = ["cloud106", "cloud107", "cloud108"]
LOCUST_MACHINES = ["cloud50", "cloud69"]
LOCUST_MACHINES_CORES = 2
SPAWN_RATES = {"1": 1, "25": 0.5, "50": 1, "75": 1.5, "100": 2}
SCENARIOS = ["staticRead", "staticWrite", "simulateUser"]

# Script flow
if __name__ == "__main__":
    # Check if there are enough input arguments
    if len(sys.argv) != 3:
        print("Invalid parameters! Usage: python3 benchmark.py <SCENARIO> <USERS>")
        sys.exit(-1)

    scenario = sys.argv[1]
    users = int(sys.argv[2])

    # Keep track of created processes
    metrics = []
    workers = []
    master = None

    # Check if input arguments are valid 
    if scenario not in SCENARIOS or str(users) not in SPAWN_RATES.keys():
        print("Invalid configuration! Check users load tier and scenario!")
        sys.exit(-1)

    # Create folder to keep test files
    print("Creating benchmark files folder...")
    folder = f"benchmarks/{scenario}_{users}_{int(time())}"
    os.mkdir(folder)
    os.mkdir(f"{folder}/logs")

    # Get IP in VPN (locust workers need to know where the master lives)
    print("Getting IP address...")
    ip_exec = subprocess.run(["ip","-json","-f","inet","addr","show","tun0"], capture_output=True)
    ip = json.loads(ip_exec.stdout.decode("utf-8"))[0]["addr_info"][0]["local"]

    # Start benchmark
    try:
        # Start monitoring cluster
        print("Starting monitoring tools...")
        for machine in CLUSTER_MACHINES:
            with open(f"{folder}/logs/{machine}_metrics.log", "w") as log: 
                metrics.append(subprocess.Popen(f'ssh gsd@{machine} "collectl -i 5 -c 204 -oT -scmn -P --sep ," > {folder}/{machine}_{scenario}_{users}_system.csv',
                               shell=True, stdout=log, stderr=log))

        # Start monitoring storage
        for machine in STORAGE_MACHINES:
            with open(f"{folder}/logs/{machine}_metrics.log", "w") as log: 
                metrics.append(subprocess.Popen(f'ssh gsd@{machine} "collectl -i 5 -c 204 -oT -sd --dskfilt nvme0n1 -P --sep ," > {folder}/{machine}_{scenario}_{users}_io.csv',
                               shell=True, stdout=log, stderr=log))

        # Collect some data before test starts
        print("Accumulating initial data...")
        sleep(50)

        # Start locust workers
        print("Starting Locust workers...")
        for machine in LOCUST_MACHINES:
            # Locust sugests one worker per CPU core
            for i in range(LOCUST_MACHINES_CORES):
                with open(f"{folder}/logs/{machine}_locust_worker{i}.log", "w") as log: 
                    workers.append(subprocess.Popen(f'ssh gsd@{machine} "cd benchmark/wiki; locust --conf={scenario}Worker.conf --master-host={ip}"',
                                   shell=True, stdout=log, stderr=log))

        # Start locust master
        print("Starting Locust master...")
        with open(f"{folder}/logs/locust_master.log", "w") as log:
            master = subprocess.Popen(f"locust --conf={scenario}Master.conf --users={users} --spawn-rate={SPAWN_RATES[str(users)]} \
                        --csv={folder}/locust_{scenario}_{users} --html={folder}/report.html", shell=True, stdout=log, stderr=log)

        # Check if processes are still alive
        isExecuting = True
        while(isExecuting):
            # Check ongoing processes
            aliveMetrics = sum([1 if p.poll() is None else 0 for p in metrics])
            aliveWorkers = sum([1 if p.poll() is None else 0 for p in workers])
            aliveMaster = 1 if master.poll() is None else 0

            # Print and wait 15 seconds
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Locust master ->  {1 if aliveMaster == 1 else 0}/1 | Locust workers -> {aliveWorkers}/{len(workers)} | Metrics collectors -> {aliveMetrics}/{len(metrics)}")
            isExecuting = (aliveMaster + aliveWorkers + aliveMetrics) != 0
            if isExecuting:
                sleep(15)

        # Benchmark finished
        print("Benchmark complete!")


    # If exception occurs, close all open processes
    except:
        print("Exception occured:", sys.exc_info()[0], "\nTerminating all created processes.")

        for process in metrics + workers:
            if process.poll() is None:
                terminate(process.pid)

        if master is not None:
            if master.poll() is None:
                terminate(master.pid)