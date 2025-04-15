from prefect import Flow
from prefect.blocks.system import JSON
from prefect.docker.docker_image import DockerImage

from litigation_data_mapper.cli import automatic_updates


def create_deployment(
    flow: Flow,
) -> None:
    """Create a deployment for the specified flow"""
    aws_env = "sandbox"
    image_name = "532586131621.dkr.ecr.eu-west-1.amazonaws.com/litigation-data-mapper"

    default_variables = JSON.load(f"default-job-variables-prefect-mvp-{aws_env}").value
    job_variables = {**default_variables}

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
