#! /bin/bash
pids=`ps -ef | grep "\.py" | grep -v grep | awk '{print $2}'`
if [ -n "$pids" ]; then
    kill $pids
fi

TIEBA_MANAGER_PATH="$HOME/Scripts/Tieba-Manager"
nohup python $TIEBA_MANAGER_PATH/cloud_review_hanime.py >/dev/null 2>&1 &
nohup python $TIEBA_MANAGER_PATH/cloud_review_halfprice.py >/dev/null 2>&1 &
nohup python $TIEBA_MANAGER_PATH/cloud_review_sunxc.py >/dev/null 2>&1 &
