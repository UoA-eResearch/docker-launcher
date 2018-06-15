#!/usr/bin/env python
import docker
from bottle import hook, get, post, run, redirect, request, response, default_app, static_file
import os
import time

DEFAULT_IMAGE="jupyter/datascience-notebook"
internal_port="8787/tcp"

client = docker.from_env()

def getTokenFromContainerLogs(container):
  for chunk in container.logs(stream=True):
    for line in chunk.split("\n"):
      print(line)
      index = line.find("?token=")
      if index > 0:
        token = line[index:]
        return token

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

@get('/running')
def running():
  containers = {}
  for container in client.containers.list():
    containers[container.name] = {
      "image": container.image.attrs["RepoTags"][0],
      "status": container.status,
      "ports": container.attrs["NetworkSettings"]["Ports"]
    }
  return containers

@post('/')
def index():
  imageName = request.params.get("image", DEFAULT_IMAGE)
  container = client.containers.run(imageName, publish_all_ports=True, detach = True)
  token = ""
  if "jupyter" in imageName:
    token = getTokenFromContainerLogs(container)
  container.reload()
  port = container.attrs['NetworkSettings']['Ports'].values()[0][0]['HostPort']
  print("Spawned container on port {}. Container status: {}".format(port, container.status))
  hostname = request.urlparts.netloc.replace(":" + str(request.urlparts.port), "")
  return "http://{}:{}/{}".format(hostname, port, token)

port = int(os.environ.get('PORT', 8080))

if __name__ == "__main__":
  try:
    try:
      run(host='0.0.0.0', port=port, debug=True, server='gunicorn', workers=8, reloader=True, timeout=1200)
    except ImportError:
      run(host='0.0.0.0', port=port, debug=True, reloader=True, timeout=1200)
  except Exception as e:
    logger.error(e)
    sys.stdin.readline()

app = default_app()
