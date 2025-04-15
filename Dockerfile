# checkov:skip=CKV_DOCKER_2
# checkov:skip=CKV_DOCKER_3
FROM prefecthq/prefect:2.20.7-python3.10

RUN pip install poetry

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

COPY litigation_data_mapper litigation_data_mapper
RUN poetry install
