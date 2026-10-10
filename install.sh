#!/bin/sh

#sudo mkdir -p /var/log/microdom
#sudo chmod 0777 /var/log/microdom
#sudo cp -uva etc/microdom.conf /etc

echo "Building microdom-abm docker image..."
docker build -t microdom-abm .
echo "Stop microdom-abm..."
docker stop microdom-abm
sleep 1
echo "Remove microdom-abm..."
docker rm microdom-abm
sleep 1
echo "Run microdom-abm..."
docker run -it \
  -d --restart unless-stopped \
  -e DBUSER=dompi_web \
  -e DBPASSWORD=dompi_web \
  -e DBHOST=192.168.10.32 \
  -e DBNAME=DB_DOMPIWEB \
  --name microdom-abm \
  -v /etc/microdom.conf:/app/etc/microdom.conf \
  -v /var/log/microdom:/app/logs \
  -v /var/lib/microdom/html:/app/html \
  -v /var/lib/microdom/download:/app/download \
  -p 8083:8083 microdom-abm

