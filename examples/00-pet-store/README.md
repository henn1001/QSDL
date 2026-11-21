# PetStore

## Overview

This is the checked-in generated Spring gold project for the multifile schema under `domain/`. It demonstrates domain-first packages (`app.api.*`), shared support (`app.shared.*`), order status updates, and a Pet media file overlay.

The schema declares a cursor-paginated pet search, but this example intentionally leaves `GET /api/v1/pets/search` unimplemented. It returns `501 Not Implemented`; use `GET /api/v1/pets` to list pets.

### Generated versus hand-maintained files

The schema under `domain/` is the source for the generated Spring project, bundled OpenAPI document, and baseline Flyway migration. `.qignore` protects hand-maintained files that the generator would otherwise overwrite, including the media API and controller and the order placement controller and test. The media storage service and tests, `application-properties.yaml`, and the follow-up Flyway migration are also hand-maintained, but need no `.qignore` entries because the generator does not emit them. Do not commit `storage/`, `target/`, or runtime logs.

Pet media is stored outside the database. Set `PET_MEDIA_STORAGE_DIRECTORY` (or `pet-media.storage-directory`) to choose the storage root; the default is `./storage/pet-media`. Storage keys, not arbitrary filesystem paths, are persisted and used for downloads.

Example upload/list/download flow (after starting the application; replace IDs):

```bash
curl -F pet_id=42 -F file=@photo.jpg -F media_type=image/jpeg -F filename=photo.jpg \\
  http://localhost:8080/api/v1/pets/media/upload
curl 'http://localhost:8080/api/v1/pets/media?pet_id=42'
curl -o photo.jpg 'http://localhost:8080/api/v1/pets/media/download?pet_id=42&media_id=7'
```

The overlay rejects traversal, symlinked storage paths, unsafe filenames, missing files, and uploads over 10 MiB.

### Regenerate in place

From `examples/00-pet-store/`, run:

```bash
qsdl generate spring -i domain/pet-store.qsdl -o . \
  -S title=PetStore -S group_id=app -S artifact_id=pet-store
```

Review the diff before committing. If the schema changes a contract implemented by the overlay, update the protected Java files by hand.

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
