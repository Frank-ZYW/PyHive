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
sudo docker run -d -p 9000:9000 -v ~/pyhive:/app/pyhive frankzyw/pyhive:latest
```

the server will be ready on localhost:9000



## Explanation

dockerfile

```dockerfile
FROM python:3.7-slim-stretch
WORKDIR /app
COPY . /app/source
COPY ./docker/run.sh /app/run.sh

# add new apt source (aliyun)
RUN cd /app/source \
    && mv /etc/apt/sources.list /etc/apt/sources.list.bakup \
    && mv ./docker/sources.list /etc/apt/

# install gcc
RUN apt-get update -y \
    && apt-get install -y gcc

# install nginx and replace config file
RUN apt-get install -y curl gnupg2 ca-certificates lsb-release \
    && echo "deb http://nginx.org/packages/debian `lsb_release -cs` nginx" | tee /etc/apt/sources.list.d/nginx.list \
    && curl -fsSL https://nginx.org/keys/nginx_signing.key | apt-key add - \
    && apt-get update -y \
    && apt-get install -y nginx \
    && apt-get clean
RUN cd /app/source \
    && mv -f ./docker/default.conf /etc/nginx/conf.d/

# add new PyPI source (Tsinghua University) and install dependencies
RUN cd /app/source \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple .

# remove useless source files
RUN rm -rf /app/source

# init pyhive
RUN cd /app \
    && pyhive init \
    && cd pyhive \
    && pyhive migrate \
    && pyhive initadmin \
    && pyhive collectstatic

# edit permission
RUN chmod a+x /app/run.sh

VOLUME /app/pyhive
CMD /bin/bash /app/run.sh
```