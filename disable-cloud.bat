@echo off
echo Disabling Pulumi Cloud and configuring local state only...

REM Set environment variable to disable cloud
set PULUMI_BACKEND_URL=file://~/.pulumi/state

REM Login to local state
pulumi login --local

echo Pulumi Cloud disabled. All state will be stored locally.
echo State location: ~/.pulumi/state
