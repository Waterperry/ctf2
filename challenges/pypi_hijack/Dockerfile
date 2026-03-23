FROM ghcr.io/astral-sh/uv:python3.11-alpine

ARG PYPI_PORT="8080"
ENV PYPI_PORT=${PYPI_PORT}

COPY loop.sh /root
COPY run.sh /root
COPY flag.txt /root
COPY pyproject_postfix.txt /root

RUN mkdir -p /root/server/packages
RUN chmod +x /root/loop.sh
RUN chmod +x /root/run.sh
RUN uv pip install --system pypiserver

COPY sample_package_set/*.whl /root/server/packages

EXPOSE ${PYPI_PORT}

ENTRYPOINT /root/run.sh
