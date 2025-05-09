# AWS EC2 Pricing MCP Server
[![Docker Pulls](https://img.shields.io/docker/pulls/ai1st/aws-pricing-mcp)](https://hub.docker.com/r/ai1st/aws-pricing-mcp) [![smithery badge](https://smithery.ai/badge/@trilogy-group/aws-pricing-mcp)](https://smithery.ai/server/@trilogy-group/aws-pricing-mcp)

The **AWS EC2 Pricing MCP Server** lets any LLM or automation script query real-time EC2 pricing with one call. Powered by a pre-parsed AWS pricing catalogue, it answers questions such as

```What is the cheapest EC2 instance with 32GB RAM?```

```Which AMD instances have more than 3.5 Ghz CPUs?```

```What is the 3-yr All Upfront discount on r6g family in eu-west-1?```

```What is the cheapest instance to run Windows with SQL Server Enterprise?```

## Using Docker

### Using a Docker hub image

Use this mcp_config.json for Docker hub image:

```json
{
  "mcpServers": {
    "AWS EC2 Pricing MCP": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-q", "--network", "none", "ai1st/aws-pricing-mcp"]
    }
  }
}
```
- The `--rm` flag removes the container when it exits.
- The `-i` flag enables interactive mode for stdio communication.
- The `-q` flag suppresses the docker messages about downloading the image.
- The `--network none` totally disconnects the container from the network to guarantee no data exfiltration.

### Using a local image

Build the image:

```bash
docker build -t aws-pricing-mcp . --build-arg BUILD_DATE=$(date +%Y-%m-%d)
```
This will download the pricing data and build the image. The BUILD_DATE parameter ensures the fresh pricing data is downloaded during build.

Sample mcp_config.json for a locally built image:

```json
{
  "mcpServers": { "AWS EC2 Pricing MCP": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--network", "none", "aws-pricing-mcp"]
    }
  }
}
```

- The `--rm` flag removes the container when it exits.
- The `-i` flag enables interactive mode for stdio communication.
- The `--network none` totally disconnects the container from the network to guarantee no data exfiltration.

## Using Python directly

You'll need to download the pricing data first:

```bash
curl https://cloudfix-public-aws-pricing.s3.us-east-1.amazonaws.com/pricing/ec2_pricing.json.gz | gunzip > ec2_pricing.json
```

It should be in the same directory as server.py.

Sample mcp_config.json for local Python:

```json
{
  "mcpServers": { "AWS EC2 Pricing MCP": {
      "command": "python",
      "args": [
        "/path/to/server.py"
      ]
    }
  }
}
```


## Building Instructions

For instructions on building and publishing the Docker image, see [BUILD.md](BUILD.md).

## Pricing Data JSON Format

See [PRICING.md](PRICING.md).
