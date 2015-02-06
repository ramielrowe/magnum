#!/bin/sh

. /etc/sysconfig/heat-params

for service in $WAIT_SERVICES; do
	echo "waiting on service $service"
	systemctl start $service
done

echo "notifying heat"
curl -sf -X PUT -H 'Content-Type: application/json' \
	--data-binary '{"Status": "SUCCESS",
	"Reason": "Setup complete",
	"Data": "OK", "UniqueId": "00000"}' \
	"$WAIT_HANDLE"
