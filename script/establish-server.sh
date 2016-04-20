#/bin/bash

sudo apt-get install curl
curl -sSL http://acs-public-mirror.oss-cn-hangzhou.aliyuncs.com/docker-engine/internet | sh -
echo "DOCKER_OPTS=\"--registry-mirror=https://n5fb0zgg.mirror.aliyuncs.com\"" | sudo tee -a /etc/default/docker
service docker restart
docker login --username=己美网络 registry.aliyuncs.com

# docker run --rm --volumes-from=static -e TARGET=production registry.aliyuncs.com/xiaolu-img/xiaolusys:latest python manage.py collectstatic --noinput
#.drone.sec 设置
#environment:
#  DOCKER_USERNAME: 己美网络
#  DOCKER_PASSWORD: ***
#  DOCKER_EMAIL: ***@xiaolu.so
# 添加数据访问白名单
# 添加xiaolusys对应的drone Public Key 到本地ssh authorizen_keys
# 修改.drone.yml 添加当前主机host
# 配置nginx site.conf 添加当前域名
# 配置xiaolusys oneapm-ci-agent 

