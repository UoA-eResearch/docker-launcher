#!/usr/bin/env python
import docker
from bottle import get, run, redirect, request, default_app

image="rocker/tidyverse"
internal_port="8787/tcp"

client = docker.from_env()

@get('/')
def index():
  # None = random host port
  container = client.containers.run(image, ports={internal_port: None}, detach = True)
  container.reload()
  port = container.attrs['NetworkSettings']['Ports'][internal_port][0]['HostPort']
  print("Spawned container on port {}. Container status: {}".format(port, container.status))
  hostname = request.urlparts.netloc.replace(":" + str(request.urlparts.port), "")
  redirect("http://{}:{}".format(hostname, port))

application = default_app()

if __name__ == "__main__":
  run(host='0.0.0.0', port=3040)
