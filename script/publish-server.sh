#!/bin/bash
################################################
#cd /var/www/deploy/taobao/taobao-backend/shopmanager
#git pull origin master
#\cp -r -a ../prod_settings.py .
#python manager.py collectstatic
#supervisorctl restart gunicorn
#supervisorctl restart celery
################################################

PUBLISH_HOST=(
root@youni.huyi.so 
root@sale.huyi.so 
root@proxy.huyi.so
)

CMD="cd /var/www/deploy/taobao/taobao-backend/shopmanager && git pull origin master && \cp -r -a ../prod_settings.py . && python manager.py collectstatic && supervisorctl restart gunicorn &&  (supervisorctl restart celery || true)" 

#CMD="lsb_release -a"

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Usage: $0 ($CMD)" >&2
  exit 1
fi

for i in "${PUBLISH_HOST[@]}"; 
do
     echo -e '..................Start publish server:' $i 
     ssh $i $CMD || exit 1
done
 
cat <<EOF
Publish server code success.
EOF