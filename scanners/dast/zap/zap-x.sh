#!/bin/sh
export DISPLAY=:1.0

export JAVA_TOOL_OPTIONS="-Dhttp.proxyHost=proxywebsrv.tech.sits.credit-agricole.fr -Dhttp.proxyPort=8080 -Dhttps.proxyHost=proxywebsrv.tech.sits.credit-agricole.fr -Dhttps.proxyPort=8080"

if [ ! -f /tmp/.X1-lock ]
then
  Xvfb :1 -screen 0 1024x768x16 -ac &
fi
/zap/zap.sh "$@"
