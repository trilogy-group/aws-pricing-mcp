import json
import boto3
import base64
import urllib.parse
import secrets
import hashlib

SESSION_NAME = "ec2-pricing-mcp"
SALT = "aws-pricing-mcp don't tell anyone"

def resolve_customer(event):
    try:
        body = base64.b64decode(event["body"])
        body = urllib.parse.parse_qs(body.decode())

        print("Decoded body:", json.dumps(body, indent=4, default=str))

        mp_session = assume_role(
            boto3.client("sts"), 386688329531, "CloudFix-RightSpend-Marketplace-Role"
        )

        print("Assumed role")

        reg_token = body["x-amzn-marketplace-token"][0]
        mp_client = mp_session.client("meteringmarketplace")
        return mp_client.resolve_customer(RegistrationToken=reg_token)
    except Exception as e:
        print("Error resolving customer", e)
        return {
            "ProductCode": "NoTokenProvided",
            "CustomerIdentifier": secrets.token_hex(4),
            "CustomerAWSAccountId": secrets.token_hex(6),
        }

    
def assume_role(sts, account, role_name, external_id=""):
    """Assume a given role using provided STS client."""
    role_arn = f"arn:aws:iam::{account}:role/{role_name}"
    params = {}
    if external_id:
        params = {"ExternalId": external_id}
    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=SESSION_NAME,
        DurationSeconds=900,
        **params,
    )
    return boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    )

def lambda_handler(event, context):
    """Route Lambda requests based on properties of the event."""
    print(json.dumps(event))
    if "Records" in event:
        return {
            "statusCode": 501,
            "body": "Cannot handle SNS events"
        }

    request_context = event.get("requestContext", {})
    http_info = request_context.get("http", {})
    path = http_info.get("path", "")
    method = http_info.get("method", "")
    if path == "/subscribe":
        customer_data = resolve_customer(event)
        identifier = customer_data.get("CustomerIdentifier", "")
        api_token = hashlib.sha256((SALT + identifier).encode("utf-8")).hexdigest()
        with open("subscribe.html") as file:
            page_html = file.read()
            page_html = page_html.replace("CUSTOMER_DATA", json.dumps(customer_data))
            page_html = page_html.replace("API_TOKEN", api_token)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": page_html
        }
    else:
        return {
            "statusCode": 404,
            "body": "Not found"
        }