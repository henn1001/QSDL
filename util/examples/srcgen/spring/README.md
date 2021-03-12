# SpringBootApp

## Overview


### Features

* * *

## Requirements

-   [JDK 11](https://www.oracle.com/java/technologies/javase-downloads.html#JDK11) or [OpenJDK 11](https://openjdk.java.net/install/)

## Running the application

Running the service(s) is as simple as starting the jar file:

    java -jar app.jar

## Configuration

* * *

The following configuration parameters are available for changing via a environment variable or a spring parameter.

-   Example

* * *

-   `SPRING_PORT` - `(server.port)` (Optional) Used port for this Service. The default is `8080`.

-   `SPRING_SSL` - `(server.ssl.enabled)` (Optional) Enables https for the service. The default is `false`.

-   `SPRING_SSL_TYPE` - `(server.ssl.key-store-type)` (Optional) The type of keystore. The default is `pkcs12`.

-   `SPRING_SSL_STORE` - `(server.ssl.key-store)` (Optional) Path to the keystore file. The default is `classpath:keystore.p12`.

-   `SPRING_SSL_STORE_PASSWORD` - `(server.ssl.key-store-password)` (Optional) The password for the keystore. The default is `password`.

-   `SPRING_SSL_ALIAS` - `(server.ssl.key-alias)` (Optional) Alias for the cert within the keystore. The default is `alias`.