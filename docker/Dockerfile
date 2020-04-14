FROM python:3.7-slim-stretch
WORKDIR /app
COPY . /app/source
COPY ./docker/run.sh /app/run.sh
RUN cd /app/source \
    && mv /etc/apt/sources.list /etc/apt/sources.list.bakup \
    && mv ./docker/sources.list /etc/apt/
RUN apt-get update -y \
    && apt-get install -y gcc
RUN apt-get install -y curl gnupg2 ca-certificates lsb-release \
    && echo "deb http://nginx.org/packages/debian `lsb_release -cs` nginx" | tee /etc/apt/sources.list.d/nginx.list \
    && curl -fsSL https://nginx.org/keys/nginx_signing.key | apt-key add - \
    && apt-get update -y \
    && apt-get install -y nginx \
    && apt-get clean
RUN cd /app/source \
    && mv -f ./docker/default.conf /etc/nginx/conf.d/
RUN cd /app/source \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple .
RUN rm -rf /app/source
RUN cd /app \
    && pyhive init \
    && cd pyhive \
    && pyhive migrate \
    && pyhive initadmin \
    && pyhive collectstatic
RUN chmod a+x /app/run.sh
VOLUME /app/pyhive
CMD /bin/bash /app/run.sh