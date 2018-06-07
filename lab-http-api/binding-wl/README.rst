# Wolfram Language Interface to the SynthAI Lab

Usage of this package assumes the SynthAI Lab (https://github.com/synthai/lab) is installed, and the Lab HTTP Server (https://github.com/synthai/lab-http-api) is running.

## General Information
Load the `LabEnvironment` package:
```
Get["path/to/lab_http_client.wl"]
```
Once the package is loaded, a list of all exposed functions can be obtained via:
```
Names["LabEnvironment`*"]
```
Obtain documentation for a specific package function:
```
?EnvCreate
```

## Running the Example Agent
For an example on how to use this package, see the Wolfram Script `example_agent.wl`.
This can be run via:
```
wolframscript -script path/to/example_agent.wl
```

