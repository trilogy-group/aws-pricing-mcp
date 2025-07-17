# AWS Pricing MCP

A Model Context Protocol (MCP) server that provides AWS EC2 instance pricing data. This project includes both a traditional server implementation and a serverless Lambda function.

## Quick Start

### Lambda Deployment (Recommended)

The Lambda function provides the same functionality as the server but with serverless benefits:

```bash
# Build and deploy
sam build
sam deploy --guided

# Get the Function URL
aws cloudformation describe-stacks \
  --stack-name aws-pricing-mcp \
  --query 'Stacks[0].Outputs[?OutputKey==`FunctionUrl`].OutputValue' \
  --output text
```

For detailed Lambda documentation, see [LAMBDA.md](LAMBDA.md).

### Server Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python src/server.py
```

## Features

- **EC2 Pricing Data**: Find the cheapest EC2 instances based on specifications
- **Multiple Pricing Models**: On Demand, Reserved Instances, CloudFix RightSpend
- **Flexible Filtering**: Region, platform, tenancy, vCPU, RAM, GPU, etc.
- **JSON-RPC 2.0**: Full MCP protocol compliance
- **Serverless Option**: Lambda function with Function URL
- **Dynamic Data**: Always up-to-date pricing from S3

## Documentation

- [LAMBDA.md](LAMBDA.md) - Comprehensive Lambda documentation
- [MCP.md](MCP.md) - MCP protocol examples
- [PRICING.md](PRICING.md) - Pricing data format and sources
- [BUILD.md](BUILD.md) - Build instructions

## License

[LICENSE](LICENSE)
