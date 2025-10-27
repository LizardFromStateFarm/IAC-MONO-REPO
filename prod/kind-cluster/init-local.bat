@echo off
echo Initializing Pulumi with local state for prod kind-cluster...

REM Ensure we're using local state
pulumi login --local

REM Create a unique state file for this tool/environment
if not exist ".\state" mkdir ".\state"

REM Initialize the stack with local state
pulumi stack init prod

echo Local state initialized for prod kind-cluster
echo State file: .\state\prod-kind-cluster.json
