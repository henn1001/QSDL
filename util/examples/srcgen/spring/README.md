# SpringBootApp

## Overview


### Features

* * *

## Requirements

-   [graalvm 21](https://www.graalvm.org/release-notes/JDK_21/)
-   [Maven](https://maven.apache.org/)

I can recommend using sdkman for the installation.

```
curl -s "https://get.sdkman.io" | bash
source ~/.sdkman/bin/sdkman-init.sh

sdk install java 21-graalce
sdk install maven
```

## Development

Bootstrap vscode by installing the recommended plugins and running the following commands:

```
cp .vscode/settings.json.template .vscode/settings.json
cp .vscode/launch.json.template .vscode/launch.json
```


## Running the application

Running the service(s) is as simple as starting the jar file:

    java -jar app.jar

## Configuration

* * *

The following configuration parameters are available. You can either provide them as arguments when running the jar or as enviroment variables.


-   `--server.port` (Optional) Used port for this Service. The default is `8080`.
