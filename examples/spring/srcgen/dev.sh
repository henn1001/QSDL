#!/bin/bash

IMAGE_NAME=app
REGISTRY=registry

build() {
  echo "building..."
  SVC_VERSION=$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)
  VERSION=${VERSION:-$SVC_VERSION}
  mvn versions:set -B -ntp -DnewVersion=${VERSION} -DgenerateBackupPoms=false
  mvn spring-boot:build-image -DskipTests -Dspring-boot.build-image.imageName=${REGISTRY}/${IMAGE_NAME}:${VERSION}
}

run() {
  echo "testing..."
  docker-compose up
}

deploy() {
  echo "deploy images..."
  docker tag $(IMAGE_NAME) $(REGISTRY)/$(IMAGE_NAME):latest
  docker push $(REGISTRY)/$(IMAGE_NAME)
}

clean() {
  echo "cleaning..."
  docker-compose down
}

# Dynamically dispatch to functions
if false; then
  echo
elif declare -F "$1" >/dev/null && [[ "$1" != _* ]]; then
  "$@"
else
  echo "Usage: $(basename "$0") [OPTIONS]"
  echo
  echo -e "\033[1;4;32m""Options:""\033[0;34m"
  compgen -A function | grep -v '^_'
  echo -e "\033[0m"
fi
