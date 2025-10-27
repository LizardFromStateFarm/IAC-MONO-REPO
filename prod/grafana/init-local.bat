@echo off
echo Initializing Pulumi with local state for prod grafana...

REM Ensure we're using local state
pulumi login --local

REM Create a unique state file for this tool/environment
if not exist ".\state" mkdir ".\state"

REM Initialize the stack with local state
pulumi stack init prod

echo Local state initialized for prod grafana
echo State file: .\state\prod-grafana.json
