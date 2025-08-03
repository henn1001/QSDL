FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

COPY src ./src
COPY README.md .
COPY pyproject.toml .
COPY uv.lock .

RUN uv tool install .

WORKDIR /generated_content

ENTRYPOINT ["qsdl"]
CMD ["--help"]

## To generate a Spring app from the input.qsdl in UNIX-like OS ##
# docker run -v $(pwd):/generated_content --user $(id -u $(whoami)):$(id -g $(whoami)) \
#   -it qsdl -g spring ./examples/openapi/input.qsdl
## To generate a Spring app from the input.qsdl in Windows ##
# docker run -v ${pwd}:/generated_content -it qsdl -g spring ./examples/openapi/input.qsdl