# SpringBootApp

## Overview


### Features

* * *

## Requirements

-   [graalvm 25](https://www.graalvm.org/release-notes/JDK_25/)
-   [Maven](https://maven.apache.org/)

I can recommend using sdkman for the installation.

```
curl -s "https://get.sdkman.io" | bash
source ~/.sdkman/bin/sdkman-init.sh

sdk install java 25-graalce
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

## Running with Maven

The application uses the in-memory H2 database by default. Select the PostgreSQL profile when running against PostgreSQL:

```bash
mvn spring-boot:run
mvn spring-boot:run -Dspring-boot.run.profiles=h2
mvn spring-boot:run -Dspring-boot.run.profiles=postgres
```

The `postgres` profile expects PostgreSQL at `localhost:5432`. The generated `docker-compose.yml` starts the application and PostgreSQL together.

## Configuration

* * *

The following configuration parameters are available. You can either provide them as arguments when running the jar or as enviroment variables.


-   `--server.port` (Optional) Used port for this Service. The default is `8080`.
