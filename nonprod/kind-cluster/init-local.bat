@echo off
echo Initializing Pulumi with local state for nonprod kind-cluster...

REM Ensure we're using local state
pulumi login --local

REM Create a unique state file for this tool/environment
if not exist ".\state" mkdir ".\state"

REM Initialize the stack with local state
pulumi stack init nonprod

echo Local state initialized for nonprod kind-cluster
echo State file: .\state\nonprod-kind-cluster.json
