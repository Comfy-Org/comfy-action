# comfy-action

[![Verify GitHub Action YML](https://github.com/Comfy-Org/comfy-action/actions/workflows/verify-action.yml/badge.svg)](https://github.com/Comfy-Org/comfy-action/actions/workflows/verify-action.yml)

Sets up ComfyUI on Github Action Runner and execute a workflow json.

This is meant to be run in the ComfyUI repository.

### TODO

[] Have option to compare results with previous runs.

### Set up MacOS Runners

Make sure Homebrew is on the path for bash. This is needed for tmate-action, which can be helpful during debugging.

`nano ~/.bash_profile`

```
export HOMEBREW_PREFIX="/opt/homebrew";
export HOMEBREW_CELLAR="/opt/homebrew/Cellar";
export HOMEBREW_REPOSITORY="/opt/homebrew";
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin${PATH+:$PATH}";
export MANPATH="/opt/homebrew/share/man${MANPATH+:$MANPATH}:";
export INFOPATH="/opt/homebrew/share/info:${INFOPATH:-}";
```
