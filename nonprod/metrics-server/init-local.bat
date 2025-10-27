@echo off
echo Initializing Pulumi with local state for nonprod metrics-server...

REM Ensure we're using local state
pulumi login --local

REM Create a unique state file for this tool/environment
if not exist ".\state" mkdir ".\state"

REM Initialize the stack with local state
pulumi stack init nonprod

echo Local state initialized for nonprod metrics-server
echo State file: .\state\nonprod-metrics-server.json
