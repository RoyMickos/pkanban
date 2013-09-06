#!/usr/bin/env bash
PROCESSIDS=$(ps -f | grep runserver | awk '{print $2}')
# the above will usually contain at least 2 id's, because the above command
# itself also contains the keyword we are after. Hence let's take a closer
# look at the process id's. The other has usually vanished at this point
#echo "Found id's: $PROCESSIDS"
for id in $PROCESSIDS; do
#	ps -f $id
	DUDE=$(ps -f $id | grep '/usr/bin/python' | awk '{print $2}')
#	echo $DUDE
	if [ $DUDE > 0 ]; then
		PID=$DUDE
		break
	fi
done
echo "Killing $PID..."
kill "$PID"
exit 0



