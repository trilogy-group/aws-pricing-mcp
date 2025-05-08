# Building the AWS EC2 Pricing MCP Server

To build the Docker image for multiple platforms (e.g., x86_64 and ARM64):

1. Enable Docker BuildKit:
```bash
export DOCKER_BUILDKIT=1
```

2. Create a builder that supports multi-platform builds:
```bash
docker buildx create --name multiplatform-builder --driver docker-container --use
```

3. Log in to Docker Hub:
```bash
docker login
```

4. Push the multi-platform image to Docker Hub:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ai1st/aws-pricing-mcp:latest --push .
```

