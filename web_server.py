#!/usr/bin/env python
import docker
from bottle import get, post, run, redirect, request, default_app, static_file
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
      run(host='0.0.0.0', port=port, debug=True, server='gunicorn', workers=8, reloader=True)
    except ImportError:
      run(host='0.0.0.0', port=port, debug=True, reloader=True)
  except Exception as e:
    logger.error(e)
    sys.stdin.readline()

app = default_app()
