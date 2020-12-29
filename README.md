# buildconfig

Two python programs to manage json formatted build configs
* mustache.py will apply a json formatted config to replace strings in a build config file (eg App.config for .NET development)
* mergeconfig.py will merge a local config with the enterprise config so that any new entries are reflected in the local config
