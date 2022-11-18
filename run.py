import json
import logging
import os
import subprocess
import time

logging.basicConfig(level=logging.INFO)

def run():
    # Get the name of the deployed Docker Swarm container stack from the environment.
    stack_name = os.environ.get('STACK', None)
    if stack_name is None:
        raise Exception('STACK environment variable not set')
    # Get the location of the output metrics file.
    metrics_file = os.environ.get('OUTPUT', None)
    if metrics_file is None:
        raise Exception('OUTPUT environment variable not set')

    prometheus_metrics = []

    ps_fmt = '{"id": "{{.ID}}", "name": "{{.Name}}", "image": "{{.Image}}", "node": "{{.Node}}", "desired_state": "{{.DesiredState}}", "ports": "{{.Ports}}"}'
    ps_cmd = f"docker stack ps {stack_name} --no-trunc --format '{ps_fmt}'"
    logging.info(f'Running: {ps_cmd}')
    ps = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
    ps_output = ps.stdout.strip()
    if ps.returncode != 0:
        raise Exception(f"Error running command: {ps_cmd} - {ps.stderr}")
    ps_data = [json.loads(line) for line in ps_output.splitlines()]

    # Lookup how many containers each node is running.
    nodes = set([ps['node'] for ps in ps_data])
    node_running = {node: 0 for node in nodes}
    node_shutdown = {node: 0 for node in nodes}
    for ps in ps_data:
        node = ps['node']
        if not node:
            continue
        if ps['desired_state'] == 'Running':
            node_running[node] += 1
        elif ps['desired_state'] == 'Shutdown':
            node_shutdown[node] += 1
    for node in nodes:
        prometheus_metrics.append(f'node_running_containers{{node="{node}"}} {node_running[node]}')
        prometheus_metrics.append(f'node_shutdown_containers{{node="{node}"}} {node_shutdown[node]}')

    # Lookup the state of each node.
    nodes_fmt = '{"id": "{{.ID}}", "hostname": "{{.Hostname}}", "status": "{{.Status}}", "availability": "{{.Availability}}", "manager_status": "{{.ManagerStatus}}"}'
    nodes_cmd = f"docker node ls --format '{nodes_fmt}'"
    logging.info(f'Running: {nodes_cmd}')
    nodes = subprocess.run(nodes_cmd, shell=True, capture_output=True, text=True)
    nodes_output = nodes.stdout.strip()
    if nodes.returncode != 0:
        raise Exception(f"Error running command: {nodes_cmd} - {nodes.stderr}")
    nodes_data = [json.loads(line) for line in nodes_output.splitlines()]
    for node in nodes_data:
        hostname = node['hostname']
        status = node['status']
        is_ready = 1 if status == 'Ready' else 0
        availability = node['availability']
        is_active = 1 if availability == 'Active' else 0
        manager_status = node['manager_status']
        is_leader = 1 if manager_status == 'Leader' else 0
        prometheus_metrics.append(f'node_ready{{node="{hostname}"}} {is_ready}')
        prometheus_metrics.append(f'node_active{{node="{hostname}"}} {is_active}')
        prometheus_metrics.append(f'node_leader{{node="{hostname}"}} {is_leader}')

    # Lookup the state of each service.
    services_fmt = '{"id": "{{.ID}}", "name": "{{.Name}}", "mode": "{{.Mode}}", "replicas": "{{.Replicas}}", "image": "{{.Image}}", "ports": "{{.Ports}}"}'
    services_cmd = f"docker stack services {stack_name} --format '{services_fmt}'"
    logging.info(f'Running: {services_cmd}')
    services = subprocess.run(services_cmd, shell=True, capture_output=True, text=True)
    services_output = services.stdout.strip()
    if services.returncode != 0:
        raise Exception(f"Error running command: {services_cmd} - {services.stderr}")
    services_data = [json.loads(line) for line in services_output.splitlines()]
    for service in services_data:
        replicas = service['replicas']
        # Remove the part after x/y, like (max 1 per node) or (global).
        # We only want the first part since that is the number of replicas.
        if ' ' in replicas:
            replicas = replicas.split(' ')[0]
        # Split the x/y into x and y
        replicas = replicas.split('/')
        name = service['name']
        n_replicas = replicas[0]
        n_desired_replicas = replicas[1]
        is_partially_running = int(n_replicas) < int(n_desired_replicas)
        is_down = int(n_replicas) == 0
        is_up = int(n_replicas) == int(n_desired_replicas)
        prometheus_metrics.append(f'service_replicas{{service="{name}"}} {n_replicas}')
        prometheus_metrics.append(f'service_desired_replicas{{service="{name}"}} {n_desired_replicas}')
        prometheus_metrics.append(f'service_is_partially_running{{service="{name}"}} {int(is_partially_running)}')
        prometheus_metrics.append(f'service_is_down{{service="{name}"}} {int(is_down)}')
        prometheus_metrics.append(f'service_is_up{{service="{name}"}} {int(is_up)}')

    logging.info(f'Successfully generated prometheus metrics.')

    # Write the metrics to the output file.
    with open(metrics_file, 'w') as f:
        f.write('\n'.join(prometheus_metrics))

while True:
    run()
    time.sleep(60)
