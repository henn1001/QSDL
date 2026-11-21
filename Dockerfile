FROM ghcr.io/astral-sh/uv:python3.13-alpine

RUN adduser -D -h /home/app app

USER app

WORKDIR /home/app

COPY --from=wheel / /tmp/qsdl-wheel/
COPY examples ./examples

# force uv to place its symlinks here instead of /usr/local/bin
ENV UV_TOOL_BIN_DIR=/home/app/.local/bin
ENV PATH="/home/app/.local/bin:${PATH}"

RUN uv tool install /tmp/qsdl-wheel/*.whl

WORKDIR /generated_content

ENTRYPOINT ["qsdl"]
CMD ["--help"]

## To generate a Spring app from the input.qsdl in UNIX-like OS ##
# docker run -v $(pwd):/generated_content --user $(id -u $(whoami)):$(id -g $(whoami)) \
#   -it qsdl generate spring -i /home/app/examples/00-pet-store/domain/pet-store.qsdl
## To generate a Spring app from the input.qsdl in Windows ##
# docker run -v ${pwd}:/generated_content -it qsdl generate spring -i /home/app/examples/00-pet-store/domain/pet-store.qsdl