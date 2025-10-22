import pulumi
import pulumi_aws as aws

litigation_data_mapper = aws.ecr.Repository(
    "litigation-data-mapper",
    encryption_configurations=[
        {
            "encryption_type": "AES256",
        }
    ],
    image_scanning_configuration={
        "scan_on_push": False,
    },
    image_tag_mutability="MUTABLE",
    name="litigation-data-mapper",
    region="eu-west-1",
    opts=pulumi.ResourceOptions(protect=True),
)

pulumi.export("repository_url", litigation_data_mapper.repository_url)
