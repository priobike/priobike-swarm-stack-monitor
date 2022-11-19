# Swarm Stack Monitor

This a tiny tool to monitor the status of a docker swarm stack. It will output the status as prometheus metrics into an output file. This file can be served by a webserver and scraped by prometheus. Here is an example how the metrics can be displayed in Grafana:

<img width="1560" alt="Screenshot 2022-11-18 at 13 41 37" src="https://user-images.githubusercontent.com/27271818/202707363-f9ce0bdb-2b5c-4160-800f-7b303c157d26.png">


## Quickstart

Build the Docker image:

```
docker build -t stack-monitor .
```

Run the example stack:

```
docker stack deploy -c stack.yaml stack
```

Now you can visit the Grafana dashboard at http://localhost:3000. The default username and password is `admin` and `secret`. Or, you can visit the prometheus metrics endpoint directly:

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

Apache License 2.0
