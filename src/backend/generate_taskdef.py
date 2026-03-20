#!/usr/bin/env python3
"""
Generates taskdef.json for CodeDeploy ECS blue/green deployment.

Fetches the current task definition for a given ECS service, strips
read-only fields, replaces the container image with the CodeDeploy
placeholder <IMAGE1_NAME>, and writes taskdef.json to the current directory.

Usage:
    python3 generate_taskdef.py <cluster_name> <service_name> <region>
"""

import json
import sys

import boto3


def main() -> None:
    if len(sys.argv) != 4:
        print(
            f"Usage: {sys.argv[0]} <cluster_name> <service_name> <region>",
            file=sys.stderr,
        )
        sys.exit(1)

    cluster_name, service_name, region = sys.argv[1], sys.argv[2], sys.argv[3]

    ecs = boto3.client("ecs", region_name=region)

    # Resolve current task definition ARN from the service
    svc_resp = ecs.describe_services(cluster=cluster_name, services=[service_name])
    services = svc_resp.get("services", [])
    if not services:
        print(f"Service '{service_name}' not found in cluster '{cluster_name}'", file=sys.stderr)
        sys.exit(1)

    task_def_arn = services[0]["taskDefinition"]
    print(f"  Task definition ARN: {task_def_arn}", file=sys.stderr)

    # Fetch full task definition
    td_resp = ecs.describe_task_definition(taskDefinition=task_def_arn)
    td = td_resp["taskDefinition"]

    # Strip read-only fields that would cause RegisterTaskDefinition to fail
    read_only_keys = [
        "taskDefinitionArn",
        "revision",
        "status",
        "requiresAttributes",
        "compatibilities",
        "registeredAt",
        "registeredBy",
    ]
    for key in read_only_keys:
        td.pop(key, None)

    # Replace image with CodeDeploy placeholder
    td["containerDefinitions"][0]["image"] = "<IMAGE1_NAME>"

    output_path = "taskdef.json"
    with open(output_path, "w") as f:
        json.dump(td, f, indent=2)

    print(f"  taskdef.json written ({len(td['containerDefinitions'])} container(s))", file=sys.stderr)


if __name__ == "__main__":
    main()
