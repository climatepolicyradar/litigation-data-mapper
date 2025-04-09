# checkov:skip=CKV_DOCKER_2
# checkov:skip=CKV_DOCKER_3
FROM python:3.10-slim-bullseye

COPY litigation_data_mapper litigation_data_mapper
COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

RUN poetry build

RUN version=$(grep 'version =' pyproject.toml | cut -d '"' -f 2) && \
    poetry run pip install dist/litigation_data_mapper-${version}-py3-none-any.whl

WORKDIR /litigation_data_mapper

CMD ["litigation_data_mapper", "--use-cache"]
