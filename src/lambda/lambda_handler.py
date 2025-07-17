"""
AWS Pricing MCP Lambda Handler

This Lambda function implements the Model Context Protocol (MCP) for AWS EC2 pricing data
without the fastmcp dependency. It handles JSON-RPC requests and provides tools for
finding EC2 instances based on specified criteria.
"""

import json
import os
import sys
import traceback
import gzip
import urllib.request
import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# Set up error logging
def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)

# Global variable to store pricing data
PRICING_DATA = None
PRICING_DATA_LAST_UPDATE = 0
CACHE_DURATION = 3600  # Cache for 1 hour (3600 seconds)

def download_and_cache_pricing_data():
    """
    Download pricing data from S3 and store it in memory.
    Returns the pricing data.
    """
    global PRICING_DATA, PRICING_DATA_LAST_UPDATE
    
    current_time = time.time()
    
    # Check if we have cached data that's still valid
    if PRICING_DATA is not None and (current_time - PRICING_DATA_LAST_UPDATE) < CACHE_DURATION:
        return PRICING_DATA
    
    # S3 URL for pricing data
    pricing_url = "https://cloudfix-public-aws-pricing.s3.us-east-1.amazonaws.com/pricing/ec2_pricing.json.gz"
    
    try:
        # Download the gzipped file
        log_error(f"Downloading pricing data from {pricing_url}")
        
        # Download and decompress in memory
        with urllib.request.urlopen(pricing_url) as response:
            compressed_data = response.read()
        
        # Decompress the gzipped data
        decompressed_data = gzip.decompress(compressed_data)
        
        # Parse the JSON data
        PRICING_DATA = json.loads(decompressed_data.decode('utf-8'))
        PRICING_DATA_LAST_UPDATE = current_time
        
        log_error(f"Successfully downloaded and cached pricing data. Size: {len(decompressed_data)} bytes")
        
        return PRICING_DATA
        
    except Exception as e:
        log_error(f"Failed to download pricing data: {str(e)}")
        log_error(traceback.format_exc())
        
        # If download fails and we have cached data, use it
        if PRICING_DATA is not None:
            log_error("Using cached pricing data as fallback")
            return PRICING_DATA
        
        # If all else fails, raise the original error
        raise

# Initialize pricing data on module load
try:
    download_and_cache_pricing_data()
except Exception as e:
    log_error(f"Failed to initialize pricing data: {str(e)}")
    # Don't raise here - let the handler try to download when needed

PLATFORM_TO_OP_CODE = {
    "Linux/UNIX": "",
    "Red Hat BYOL Linux": "00g0",
    "Red Hat Enterprise Linux": "0010",
    "Red Hat Enterprise Linux with HA": "1010",
    "Red Hat Enterprise Linux with SQL Server Standard and HA": "1014",
    "Red Hat Enterprise Linux with SQL Server Enterprise and HA": "1110",
    "Red Hat Enterprise Linux with SQL Server Standard": "0014",
    "Red Hat Enterprise Linux with SQL Server Web": "0210",
    "Red Hat Enterprise Linux with SQL Server Enterprise": "0110",
    "Linux with SQL Server Enterprise": "0100",
    "Linux with SQL Server Standard": "0004",
    "Linux with SQL Server Web": "0200",
    "SUSE Linux": "000g",
    "Windows": "0002",
    "Windows BYOL": "0800",
    "Windows with SQL Server Enterprise": "0102",
    "Windows with SQL Server Standard": "0006",
    "Windows with SQL Server Web": "0202",
}

PRICING_MODELS = ["On Demand", "1-yr No Upfront", "1-yr Partial Upfront", "1-yr All Upfront", "3-yr No Upfront", "3-yr Partial Upfront", "3-yr All Upfront"]
TENANCIES = ["Shared", "Dedicated"]

# MCP Server Info
SERVER_INFO = {
    "name": "AWS EC2 Pricing MCP",
    "version": "1.0.0"
}

# MCP Protocol Version
PROTOCOL_VERSION = "2025-03-26"

def create_error_response(request_id: str, code: int, message: str, data: Optional[Dict] = None) -> Dict:
    """Create a JSON-RPC error response"""
    error = {
        "code": code,
        "message": message
    }
    if data:
        error["data"] = data
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error
    }

def create_success_response(request_id: str, result: Any) -> Dict:
    """Create a JSON-RPC success response"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }

def handle_initialize(params: Dict) -> Dict:
    """Handle MCP initialize request"""
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {
            "logging": {},
            "prompts": {
                "listChanged": True
            },
            "resources": {
                "subscribe": True,
                "listChanged": True
            },
            "tools": {
                "listChanged": True
            }
        },
        "serverInfo": SERVER_INFO,
        "instructions": "AWS EC2 Pricing MCP Server - Provides tools to find EC2 instances based on pricing and specifications"
    }

def handle_ping() -> Dict:
    """Handle MCP ping request"""
    return {}

def handle_tools_list(params: Dict) -> Dict:
    """Handle MCP tools/list request"""
    tools = [
        {
            "name": "ec2_instances_pricing",
            "description": "Find AWS EC2 instances based on specified criteria including pricing, specifications, and filters",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filter_region": {
                        "type": "string",
                        "description": "AWS region (default: us-east-1)",
                        "default": "us-east-1"
                    },
                    "filter_platform": {
                        "type": "string",
                        "description": "OS platform",
                        "enum": list(PLATFORM_TO_OP_CODE.keys()),
                        "default": "Linux/UNIX"
                    },
                    "filter_tenancy": {
                        "type": "string",
                        "description": "Instance tenancy",
                        "enum": TENANCIES,
                        "default": "Shared"
                    },
                    "filter_pricing_model": {
                        "type": "string",
                        "description": "Pricing model",
                        "enum": PRICING_MODELS,
                        "default": "On Demand"
                    },
                    "filter_min_vcpu": {
                        "type": "integer",
                        "description": "Minimum number of vCPUs",
                        "default": 0
                    },
                    "filter_min_ram": {
                        "type": "number",
                        "description": "Minimum amount of RAM in GB",
                        "default": 0
                    },
                    "filter_min_gpu": {
                        "type": "integer",
                        "description": "Minimum number of GPUs",
                        "default": 0
                    },
                    "filter_min_gpu_memory": {
                        "type": "integer",
                        "description": "Minimum GPU memory in GB",
                        "default": 0
                    },
                    "filter_min_cpu_ghz": {
                        "type": "number",
                        "description": "Minimum CPU clock speed in GHz",
                        "default": 0
                    },
                    "filter_min_network_performance": {
                        "type": "integer",
                        "description": "Minimum network performance in Mbps",
                        "default": 0
                    },
                    "filter_min_ebs_throughput": {
                        "type": "integer",
                        "description": "Minimum dedicated EBS throughput in Mbps",
                        "default": 0
                    },
                    "filter_min_ephemeral_storage": {
                        "type": "integer",
                        "description": "Minimum ephemeral storage in GB",
                        "default": 0
                    },
                    "filter_max_price_per_hour": {
                        "type": "number",
                        "description": "Maximum price per hour in USD",
                        "default": None
                    },
                    "filter_family": {
                        "type": "string",
                        "description": "Filter by instance family (e.g., 'm5', 'c6g')",
                        "default": ""
                    },
                    "filter_size": {
                        "type": "string",
                        "description": "Filter by instance size (e.g., 'large', '2xlarge')",
                        "default": ""
                    },
                    "filter_processor": {
                        "type": "string",
                        "description": "Filter by physical processor (e.g., 'Graviton', 'Xeon', 'AMD')",
                        "default": ""
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Field to sort by",
                        "enum": ["Price", "Clock Speed GHz", "vCPU cores", "Memory GB", "Ephemeral Storage GB", "Network Performance Mbps", "Dedicated EBS Throughput Mbps", "GPU cores", "GPU Memory GB"],
                        "default": "Price"
                    },
                    "sort_order": {
                        "type": "string",
                        "description": "Sort order",
                        "enum": ["Ascending", "Descending"],
                        "default": "Descending"
                    },
                    "page_num": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0
                    }
                }
            }
        }
    ]
    
    return {
        "tools": tools
    }

def ec2_instances_pricing(
    filter_region: str = "us-east-1",
    filter_platform: str = "Linux/UNIX",
    filter_tenancy: str = "Shared",
    filter_pricing_model: str = "On Demand",
    filter_min_vcpu: int = 0,
    filter_min_ram: float = 0,
    filter_min_gpu: int = 0,
    filter_min_gpu_memory: int = 0,
    filter_min_cpu_ghz: float = 0,
    filter_min_network_performance: int = 0,
    filter_min_ebs_throughput: int = 0,
    filter_min_ephemeral_storage: int = 0,
    filter_max_price_per_hour: Optional[float] = None,
    filter_family: str = "",
    filter_size: str = "",
    filter_processor: str = "",
    sort_by: str = "Price",
    sort_order: str = "Descending",
    page_num: int = 0
) -> List[Dict[str, Any]]:
    """
    Find AWS EC2 instances based on specified criteria.
    
    Returns:
    - List of instances matching the criteria (5 per page). CloudFix RightSpend pricing is provided when using the flexible cRIs provided by RightSpend (a third-party solution). The benefit of RightSpend is that it 1) eliminates the need for complex forecasting or frequent consultations with engineering about usage fluctuations 2) removes the risk of unused reservations 3) provides 3-yr All Upfront discounts without the need for prepayment.
    """
    global PRICING_DATA
    
    # Ensure we have pricing data
    if PRICING_DATA is None:
        try:
            download_and_cache_pricing_data()
        except Exception as e:
            raise RuntimeError(f"Failed to load pricing data: {str(e)}")
    
    # Get the operation code for the platform
    if filter_platform not in PLATFORM_TO_OP_CODE:
        raise ValueError(f"Invalid platform: {filter_platform}; valid platforms: {list(PLATFORM_TO_OP_CODE.keys())}")
    filter_op_code = PLATFORM_TO_OP_CODE.get(filter_platform, "")

    if filter_tenancy not in TENANCIES:
        raise ValueError(f"Invalid tenancy: {filter_tenancy}; valid tenancies: {list(TENANCIES)}")
    
    if filter_pricing_model not in PRICING_MODELS:
        raise ValueError(f"Invalid pricing model: {filter_pricing_model}; valid pricing models: {list(PRICING_MODELS)}")
    
    # Find matching instances
    on_demand_price_offset = 7 * TENANCIES.index(filter_tenancy)
    price_offset = on_demand_price_offset + PRICING_MODELS.index(filter_pricing_model)
    
    matching_instances = []
    
    for family_name, family in PRICING_DATA.items():
        # Filter by family if specified
        if filter_family and family_name != filter_family:
            continue
            
        # Filter by processor if specified
        if filter_processor and filter_processor.lower() not in family.get("Physical Processor", "").lower():
            continue
            
        if family["Clock Speed, GHz"] < filter_min_cpu_ghz:
            continue
                
        for size_name, size in family["sizes"].items():
            # Filter by size if specified
            if filter_size and size_name != filter_size:
                continue
                
            # Check if the instance meets the minimum requirements
            if size.get("vCPU, cores", 0) < filter_min_vcpu:
                continue
                
            if size.get("Memory, GB", 0) < filter_min_ram:
                continue
                
            if size.get("GPU, cores", 0) < filter_min_gpu:
                continue
                
            if size.get("GPU Memory, GB", 0) < filter_min_gpu_memory:
                continue
                
            if size.get("Network Performance, Mbps", 0) < filter_min_network_performance:
                continue
                
            if size.get("Dedicated EBS Throughput, Mbps", 0) < filter_min_ebs_throughput:
                continue
                
            if size.get("Ephemeral Storage, GB", 0) < filter_min_ephemeral_storage:
                continue
        
            if "operations" not in size:
                raise ValueError(f"Instance {family_name}.{size_name} does not have operations")
            for op_code, regions in size["operations"].items():
                if op_code != filter_op_code:
                    continue

                for region, prices in regions.items():
                    if region != filter_region:
                        continue

                    price_arr = prices.split(",")
                    if len(price_arr) < price_offset:
                        continue

                    price = price_arr[price_offset]
                    if price == "":
                        continue

                    on_demand_price = price_arr[on_demand_price_offset]

                    instance = {
                        "Instance Type": f"{family_name}.{size_name}",
                        "Region": filter_region,
                        "Platform": filter_platform,
                        "Tenancy": filter_tenancy,
                        "Pricing Model": filter_pricing_model,
                        "Effective Price per hour, USD": float(price),
                        "Effective Price per month, USD": round(float(price) * 24 * 365 / 12, 2),
                        "Effective Price per year, USD": round(float(price) * 24 * 365, 2)
                    }
                    if filter_pricing_model == "1-yr Partial Upfront":
                        instance["Upfront Payment, USD"] = round(float(price) * 24 * 365 / 2, 2)
                    elif filter_pricing_model == "1-yr All Upfront":
                        instance["Upfront Payment, USD"] = round(float(price) * 24 * 365, 2)
                    elif filter_pricing_model == "3-yr Partial Upfront":
                        instance["Upfront Payment, USD"] = round(float(price) * 24 * 365 * 3 / 2, 2)
                    elif filter_pricing_model == "3-yr All Upfront":
                        instance["Upfront Payment, USD"] = round(float(price) * 24 * 365 * 3, 2)
                        
                    if on_demand_price and on_demand_price != price:
                        instance["On-Demand Price per hour, USD"] = float(on_demand_price)
                        instance["Discount Percentage"] = (1 - (float(price) / float(on_demand_price))) * 100

                    if len(price_arr) > on_demand_price_offset+6:
                        cloudfix_rightspend_price = price_arr[on_demand_price_offset+6]
                        if cloudfix_rightspend_price != "":
                            instance["CloudFix RightSpend Price per hour, USD"] = float(cloudfix_rightspend_price)
                            instance["CloudFix RightSpend Price per month, USD"] = round(float(cloudfix_rightspend_price) * 24 * 365 / 12, 2)
                            instance["CloudFix RightSpend Price per year, USD"] = round(float(cloudfix_rightspend_price) * 24 * 365, 2)
                            instance["CloudFix RightSpend Upfront Payment, USD"] = round(float(cloudfix_rightspend_price) * 24 * 7, 2)
                    instance.update({key: value for key, value in family.items() if key != "sizes"})
                    instance.update({key: value for key, value in size.items() if key != "operations"})
            
                    matching_instances.append(instance)
    
    # Filter by max price if specified
    if filter_max_price_per_hour is not None:
        matching_instances = [i for i in matching_instances if i["Effective Price per hour, USD"] <= filter_max_price_per_hour]

    # Define sort key mapping
    sort_key_map = {
        "Price": "Effective Price per hour, USD",
        "Clock Speed GHz": "Clock Speed, GHz",
        "vCPU cores": "vCPU, cores",
        "Memory GB": "Memory, GB",
        "Ephemeral Storage GB": "Ephemeral Storage, GB",
        "Network Performance Mbps": "Network Performance, Mbps",
        "Dedicated EBS Throughput Mbps": "Dedicated EBS Throughput, Mbps",
        "GPU cores": "GPU, cores",
        "GPU Memory GB": "GPU Memory, GB"
    }

    # Sort by selected field
    if sort_by not in sort_key_map:
        raise ValueError(f"Invalid sort by: {sort_by}; valid sort by: {list(sort_key_map.keys())}")
    sort_key = sort_key_map.get(sort_by, "Effective Price per hour, USD")
    
    # Two-pass sorting approach:
    # 1. First sort by price (ascending) - this will be our secondary sort
    matching_instances.sort(key=lambda x: x.get("Effective Price per hour, USD", 0))
    
    # 2. Then sort by the primary field with the specified direction
    # Since Python's sort is stable, when primary fields are equal, the price order is preserved
    matching_instances.sort(
        key=lambda x: x.get(sort_key, 0),
        reverse=(sort_order == "Descending")
    )
    
    # Calculate pagination
    items_per_page = 5
    start_idx = page_num * items_per_page
    end_idx = start_idx + items_per_page
    
    # Return the requested page
    return matching_instances[start_idx:end_idx]

def handle_tools_call(params: Dict) -> Dict:
    """Handle MCP tools/call request"""
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "ec2_instances_pricing":
            result = ec2_instances_pricing(**arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ],
                "isError": False
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }
                ],
                "isError": True
            }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing tool: {str(e)}"
                }
            ],
            "isError": True
        }

def handle_resources_list(params: Dict) -> Dict:
    """Handle MCP resources/list request"""
    return {
        "resources": []
    }

def handle_resources_read(params: Dict) -> Dict:
    """Handle MCP resources/read request"""
    return {
        "contents": []
    }

def handle_prompts_list(params: Dict) -> Dict:
    """Handle MCP prompts/list request"""
    return {
        "prompts": []
    }

def handle_prompts_get(params: Dict) -> Dict:
    """Handle MCP prompts/get request"""
    return {
        "description": "",
        "messages": []
    }

def process_mcp_request(request: Dict) -> Dict:
    """
    Process MCP protocol request and return response
    
    Args:
        request: JSON-RPC request object
    
    Returns:
        JSON-RPC response object
    """
    try:
        # Extract request details
        jsonrpc = request.get("jsonrpc")
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        # Validate JSON-RPC version
        if jsonrpc != "2.0":
            return create_error_response(
                request_id, 
                -32600, 
                "Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Handle different MCP methods
        if method == "initialize":
            result = handle_initialize(params)
            return create_success_response(request_id, result)
        
        elif method == "ping":
            result = handle_ping()
            return create_success_response(request_id, result)
        
        elif method == "tools/list":
            result = handle_tools_list(params)
            return create_success_response(request_id, result)
        
        elif method == "tools/call":
            result = handle_tools_call(params)
            return create_success_response(request_id, result)
        
        elif method == "resources/list":
            result = handle_resources_list(params)
            return create_success_response(request_id, result)
        
        elif method == "resources/read":
            result = handle_resources_read(params)
            return create_success_response(request_id, result)
        
        elif method == "prompts/list":
            result = handle_prompts_list(params)
            return create_success_response(request_id, result)
        
        elif method == "prompts/get":
            result = handle_prompts_get(params)
            return create_success_response(request_id, result)
        
        elif method == "notifications/initialized":
            # This is a notification, no response needed
            return None
        
        else:
            return create_error_response(
                request_id,
                -32601,
                f"Method not found: {method}"
            )
    
    except json.JSONDecodeError as e:
        return create_error_response(
            None,
            -32700,
            f"Parse error: {str(e)}"
        )
    
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        log_error(traceback.format_exc())
        return create_error_response(
            request_id if 'request_id' in locals() else None,
            -32603,
            f"Internal error: {str(e)}"
        )

def lambda_handler(event: Dict, context: Any) -> Dict:
    """
    AWS Lambda handler for HTTP requests via Function URL
    
    Args:
        event: Lambda event containing HTTP request details
        context: Lambda context object
    
    Returns:
        HTTP response with JSON-RPC response
    """
    try:
        # Handle CORS preflight requests
        if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Credentials": "true"
                },
                "body": ""
            }
        
        # Get the HTTP method and body
        http_method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
        body = event.get("body", "{}")
        
        # Parse the request body
        if isinstance(body, str):
            try:
                request = json.loads(body)
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "error": "Invalid JSON in request body"
                    })
                }
        else:
            request = body
        
        # Process the MCP request
        response = process_mcp_request(request)
        
        # Return HTTP response
        if response is None:
            # For notifications, return empty success
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": ""
            }
        else:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(response)
            }
    
    except Exception as e:
        log_error(f"Unexpected error in lambda_handler: {str(e)}")
        log_error(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        } 