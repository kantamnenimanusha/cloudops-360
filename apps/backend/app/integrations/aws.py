"""Read-only AWS inventory via boto3's default credential chain (IRSA / instance role / env). Disabled unless ENABLE_AWS=true."""
from datetime import datetime, timedelta, timezone

from .result import NotConfigured


def _client(s, service):
    if not s.enable_aws:
        raise NotConfigured("AWS integration disabled (ENABLE_AWS=false) - expected when running locally")
    import boto3

    return boto3.client(service, region_name=s.aws_region or None)


def ec2_instances(s):
    out = []
    for r in _client(s, "ec2").describe_instances()["Reservations"]:
        for i in r["Instances"]:
            tags = {t["Key"]: t["Value"] for t in i.get("Tags", [])}
            out.append({"id": i["InstanceId"], "type": i["InstanceType"], "state": i["State"]["Name"],
                        "name": tags.get("Name", ""), "project": tags.get("Project", ""),
                        "launch_time": i["LaunchTime"].isoformat(), "az": i["Placement"]["AvailabilityZone"]})
    return out


def ecr_repositories(s):
    ecr = _client(s, "ecr")
    out = []
    for repo in ecr.describe_repositories()["repositories"]:
        images = ecr.describe_images(repositoryName=repo["repositoryName"], maxResults=100)["imageDetails"]
        images.sort(key=lambda x: x["imagePushedAt"], reverse=True)
        out.append({"name": repo["repositoryName"], "image_count": len(images), "immutable": repo["imageTagMutability"] == "IMMUTABLE",
                    "latest_tags": (images[0].get("imageTags") or []) if images else [],
                    "latest_push": images[0]["imagePushedAt"].isoformat() if images else None})
    return out


def ec2_cpu(s, instance_ids):
    cw = _client(s, "cloudwatch")
    end = datetime.now(timezone.utc)
    out = []
    for iid in instance_ids:
        dp = cw.get_metric_statistics(Namespace="AWS/EC2", MetricName="CPUUtilization",
                                      Dimensions=[{"Name": "InstanceId", "Value": iid}], StartTime=end - timedelta(hours=1),
                                      EndTime=end, Period=300, Statistics=["Average"])["Datapoints"]
        dp.sort(key=lambda x: x["Timestamp"])
        out.append({"instance": iid, "points": [[d["Timestamp"].isoformat(), round(d["Average"], 2)] for d in dp]})
    return out
