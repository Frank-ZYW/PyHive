# Docker

## Build

change to root folder, and exec:

```shell
sudo docker build -t pyhive -f docker/Dockerfile .
```

```shell
sudo docker run -d -p 3031:3031 --restart=always pyhive:latest
```