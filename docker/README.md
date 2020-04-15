# Docker

## Build

Build image by dockerfile

```shell
# change to root folder
cd PyHive

# build image
sudo docker build -t pyhive -f docker/Dockerfile .
```



## Use

Run container from docker hub

```shell
sudo docker run -d -p 8000:8000 -v ~/pyhive:/app/pyhive frankzyw/pyhive:latest
```

the server will be ready on localhost:8000



## Explanation

dockerfile

```dockerfile
FROM python:3.7-slim-stretch
WORKDIR /app
COPY . /app/source
COPY ./docker/run.sh /app/run.sh
RUN cd /app/source \
    # add new apt source (aliyun)
    && mv /etc/apt/sources.list /etc/apt/sources.list.bakup \
    && mv ./docker/sources.list /etc/apt/ \
    && apt-get update -y \
    # install gcc nginx and replace config file
    && apt-get install -y gcc curl gnupg2 ca-certificates lsb-release \
    && echo "deb http://nginx.org/packages/debian `lsb_release -cs` nginx" | tee /etc/apt/sources.list.d/nginx.list \
    && curl -fsSL https://nginx.org/keys/nginx_signing.key | apt-key add - \
    && apt-get update -y \
    && apt-get install -y nginx \
    && apt-get clean \
    && mv -f ./docker/default.conf /etc/nginx/conf.d/ \
    # add new PyPI source (Tsinghua University) and install dependencies
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple . \
    && cd /app \
    # remove useless source files
    && rm -rf /app/source \
    # edit permission
    && chmod a+x /app/run.sh
VOLUME /app/pyhive
CMD /bin/bash /app/run.sh
```