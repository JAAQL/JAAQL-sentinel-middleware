#!/bin/bash
set -e

chmod +777 entrypoint.sh
cd "$INSTALL_PATH"

cp -r $INSTALL_PATH/www_dir/. $INSTALL_PATH/www

export PYTHONUNBUFFERED=TRUE
export PYTHONPATH=.

if [ "$LOG_TO_OUTPUT" = "TRUE" ] ; then
  echo "Logging to output"
  ln -sf /dev/stdout log/management_service.log
  ln -sf /dev/stdout log/reporting_service.log
fi

$PYPY_PATH/bin/pypy hosted_services/management_service/patch_ms.py &> log/management_service.log &
$PYPY_PATH/bin/pypy hosted_services/reporting_service/patch_rs.py &> log/reporting_service.log &

JEQL_REPLACE="import * as JEQL from '../../JEQL/JEQL.js'"
sed -ri '1s@^.*$@'"$JEQL_REPLACE"'@' $INSTALL_PATH/www/apps/sentinel/scripts/site.js

cd ../
./entrypoint.sh
