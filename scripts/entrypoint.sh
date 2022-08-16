#!/bin/bash

. /kb/deployment/user-env.sh

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  cd /data
  echo "Downloading VirSorter2 database"
  wget --no-check-certificate -O db.tgz https://osf.io/v46sc/download && tar xzf db.tgz && rm -rf db.tgz
  find /data/db -type d -exec chmod 755 {} \;
  find /data/db -type f -exec chmod 644 {} \;
#  chmod 755 /data/db/conda_envs/d8b54744
  if [[ -d "db/hmm" && -d "db/rbs" && -d "db/group" ]]; then
    echo "Database setup completed successfully"
    touch __READY__
  else
    echo "Initialization failed"
  fi

elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
