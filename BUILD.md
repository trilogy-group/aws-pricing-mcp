# Building the AWS EC2 Pricing MCP Server

## Docker Instructions

### Building the Docker Image

To build the Docker image for the AWS EC2 Pricing MCP server:

```bash
docker build -t aws-pricing-mcp .
```

### Multi-Platform Builds

To build the Docker image for multiple platforms (e.g., x86_64 and ARM64):

1. Enable Docker BuildKit:
```bash
export DOCKER_BUILDKIT=1
```

2. Create a builder that supports multi-platform builds:
```bash
docker buildx create --name multiplatform-builder --driver docker-container --use
```

3. Build and push the multi-platform image:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ai1st/aws-pricing-mcp:latest --push .
```

### Publishing to Docker Hub

To publish your image to Docker Hub:

1. Log in to Docker Hub:
```bash
docker login
```

2. Tag your image with your Docker Hub username:
```bash
docker tag aws-pricing-mcp ai1st/aws-pricing-mcp:latest
```

3. Push the image to Docker Hub:
```bash
docker push ai1st/aws-pricing-mcp:latest
```

For multi-platform publishing to Docker Hub:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ai1st/aws-pricing-mcp:latest --push .
```

