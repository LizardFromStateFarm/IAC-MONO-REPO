@echo off
echo Initializing all Pulumi tools with separate local state files...

REM First, disable cloud completely
echo Step 1: Disabling Pulumi Cloud...
call disable-cloud.bat

REM Initialize all prod tools
echo.
echo Step 2: Initializing PROD tools...
echo Initializing prod/kind-cluster...
cd prod\kind-cluster
call init-local.bat
cd ..\..

echo Initializing prod/grafana...
cd prod\grafana
call init-local.bat
cd ..\..

echo Initializing prod/metrics-server...
cd prod\metrics-server
call init-local.bat
cd ..\..

REM Initialize all nonprod tools
echo.
echo Step 3: Initializing NONPROD tools...
echo Initializing nonprod/kind-cluster...
cd nonprod\kind-cluster
call init-local.bat
cd ..\..

echo Initializing nonprod/grafana...
cd nonprod\grafana
call init-local.bat
cd ..\..

echo Initializing nonprod/metrics-server...
cd nonprod\metrics-server
call init-local.bat
cd ..\..

echo.
echo All tools initialized with separate local state files!
echo.
echo State file locations:
echo   prod/kind-cluster/state/prod-kind-cluster.json
echo   prod/grafana/state/prod-grafana.json
echo   prod/metrics-server/state/prod-metrics-server.json
echo   nonprod/kind-cluster/state/nonprod-kind-cluster.json
echo   nonprod/grafana/state/nonprod-grafana.json
echo   nonprod/metrics-server/state/nonprod-metrics-server.json
