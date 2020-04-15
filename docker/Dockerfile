FROM python:3.7-slim-stretch
WORKDIR /app
COPY . /app/source
COPY ./docker/run.sh /app/run.sh
RUN cd /app/source \
    && mv /etc/apt/sources.list /etc/apt/sources.list.bakup \
    && mv ./docker/sources.list /etc/apt/ \
    && apt-get update -y \
    && apt-get install -y gcc curl gnupg2 ca-certificates lsb-release \
    && echo "deb http://nginx.org/packages/debian `lsb_release -cs` nginx" | tee /etc/apt/sources.list.d/nginx.list \
    && curl -fsSL https://nginx.org/keys/nginx_signing.key | apt-key add - \
    && apt-get update -y \
    && apt-get install -y nginx \
    && apt-get clean \
    && mv -f ./docker/default.conf /etc/nginx/conf.d/ \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple . \
    && cd /app \
    && rm -rf /app/source \
    && chmod a+x /app/run.sh
VOLUME /app/pyhive
CMD /bin/bash /app/run.sh