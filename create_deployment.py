from prefect import Flow
from prefect.blocks.system import JSON
from prefect.docker.docker_image import DockerImage

from litigation_data_mapper.flows import automatic_updates

# TODO: Update these amounts, we have used the same configs in the knowledge graph flows
# to get this working, but should be updated accordingly as this might be too much memory
MEGABYTES_PER_GIGABYTE = 1024
DEFAULT_FLOW_VARIABLES = {
    "cpu": MEGABYTES_PER_GIGABYTE * 4,
    "memory": MEGABYTES_PER_GIGABYTE * 16,
}


def create_deployment(
    flow: Flow,
) -> None:
    """Create a deployment for the specified flow"""
    aws_env = "prod"
    image_name = "532586131621.dkr.ecr.eu-west-1.amazonaws.com/litigation-data-mapper"

    # trunk ignore
    default_variables = JSON.load(f"default-job-variables-prefect-mvp-{aws_env}").value  # type: ignore
    job_variables = {**default_variables, **DEFAULT_FLOW_VARIABLES}

    _ = flow.deploy(
        "litigation-automatic-updates-deployment",
        work_pool_name=f"mvp-{aws_env}-ecs",
        image=DockerImage(
            name=image_name,
            tag="latest",
            dockerfile="Dockerfile",
        ),
        work_queue_name=f"mvp-{aws_env}",
        job_variables=job_variables,
        build=False,
        push=False,
    )


if __name__ == "__main__":
    create_deployment(automatic_updates)
