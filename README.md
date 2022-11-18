# Swarm Stack Monitor

This a tiny tool to monitor the status of a docker swarm stack. It will output the status as prometheus metrics into an output file. This file can be served by a webserver and scraped by prometheus.

## Quickstart

Build the Docker image:

```
docker build -t stack-monitor .
```

Run the example stack:

```
docker stack deploy -c stack.yaml stack
```

Visit the prometheus metrics endpoint:

```
curl http://localhost/metrics.txt
```

This will output something like this:

```
node_running_containers{node="docker-desktop"} 3
node_shutdown_containers{node="docker-desktop"} 21
node_ready{node="docker-desktop"} 1
node_active{node="docker-desktop"} 1
node_leader{node="docker-desktop"} 1
service_replicas{service="stack_dummy"} 1
service_desired_replicas{service="stack_dummy"} 4
service_is_partially_running{service="stack_dummy"} 1
service_is_down{service="stack_dummy"} 0
service_is_up{service="stack_dummy"} 0
service_replicas{service="stack_stack-monitor"} 1
service_desired_replicas{service="stack_stack-monitor"} 1
service_is_partially_running{service="stack_stack-monitor"} 0
service_is_down{service="stack_stack-monitor"} 0
service_is_up{service="stack_stack-monitor"} 1
service_replicas{service="stack_stack-monitor-nginx"} 1
service_desired_replicas{service="stack_stack-monitor-nginx"} 1
service_is_partially_running{service="stack_stack-monitor-nginx"} 0
service_is_down{service="stack_stack-monitor-nginx"} 0
service_is_up{service="stack_stack-monitor-nginx"} 1
```

## Integrating with your stack

To integrate this tool with your stack, please check the `stack.yaml` file.

## License

MIT
