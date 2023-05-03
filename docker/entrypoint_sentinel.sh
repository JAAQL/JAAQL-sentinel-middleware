#!/bin/bash
set -e

chmod +777 entrypoint.sh
cd "$INSTALL_PATH"

if [ "$JAAQL_DEBUGGING" = "TRUE" ] ; then
  export PYTHONUNBUFFERED=TRUE
fi
export PYTHONPATH=.

if [ "$LOG_TO_OUTPUT" = "TRUE" ] ; then
  echo "Logging to output"
  ln -sf /dev/stdout log/services.log
fi

$PY_PATH hosted_services/patch_services.py &> log/services.log &

cd ../
./entrypoint.sh
