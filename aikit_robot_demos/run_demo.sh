#!/bin/bash
function cleanup() {
  xhost -local:root
  containers=$(docker container ls -f "name=demo" -aq)
  docker container stop "$containers"
  exit 1
}

demos="demos."
function main() {
  xhost +local:root
  docker run --rm -it --gpus all --net host --privileged --env NVIDIA_DISABLE_REQUIRE=1 --name "demo" --shm-size 64g\
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw -e DISPLAY -e QT_X11_NO_MITSHM=1 \
  \
  -v /home/"${USER}"/aikit_robot:/aikit_robot \
  \
  -v /home/"${USER}"/aikit/aikit:/aikit/aikit \
  -v /home/"${USER}"/aikit_demo_utils/aikit_demo_utils:/demo-utils/aikit_demo_utils \
  -v /home/"${USER}"/aikit_builder/aikit_builder:/builder/aikit_builder \
  -v /home/"${USER}"/aikit_mech/aikit_mech:/mech/aikit_mech \
  -v /home/"${USER}"/aikit_vision/aikit_vision:/vision/aikit_vision \
  \
  -v /home/"${USER}"/PyRep/pyrep:/PyRep/pyrep \
  \
   khulnasoft/aikit-robot:latest python3 -m $demos"$1" "${@:2}"
}

main "$@" || cleanup