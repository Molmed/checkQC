Bootstrap:docker
From:ubuntu:latest

%environment
LC_ALL=C.UTF-8
LANG=C.UTF-8

%setup
  rsync -r --exclude *.img $PWD $SINGULARITY_ROOTFS/

%post
  apt update -y
  apt upgrade -y
  apt install -y python3 python3-pip
  pip3 install -f https://github.com/Illumina/interop/releases/latest interop
  pip3 install /checkQC/

%runscript
  echo "Running CheckQC in Singularity container"
  exec checkqc "$@"
