"""
Test script for the AWS Pricing MCP Lambda Handler

This script demonstrates how to use the Lambda handler with sample MCP requests.
"""

import json
from lambda_handler import lambda_handler, process_mcp_request

def test_initialize():
    """Test the initialize request"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "TestClient",
                "version": "1.0.0"
            }
        }
    }
    
    # Test direct MCP processing
    response = process_mcp_request(request)
    print("Initialize Response (Direct MCP):")
    print(json.dumps(response, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test HTTP Lambda handler
    http_event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": json.dumps(request)
    }
    
    http_response = lambda_handler(http_event, None)
    print("Initialize Response (HTTP Lambda):")
    print(json.dumps(http_response, indent=2))
    print("\n" + "="*50 + "\n")

def test_tools_list():
    """Test the tools/list request"""
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    # Test direct MCP processing
    response = process_mcp_request(request)
    print("Tools List Response (Direct MCP):")
    print(json.dumps(response, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test HTTP Lambda handler
    http_event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": json.dumps(request)
    }
    
    http_response = lambda_handler(http_event, None)
    print("Tools List Response (HTTP Lambda):")
    print(json.dumps(http_response, indent=2))
    print("\n" + "="*50 + "\n")

def test_tools_call():
    """Test the tools/call request"""
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "ec2_instances_pricing",
            "arguments": {
                "filter_region": "us-east-1",
                "filter_platform": "Linux/UNIX",
                "filter_tenancy": "Shared",
                "filter_pricing_model": "On Demand",
                "filter_min_vcpu": 2,
                "filter_min_ram": 4.0,
                "filter_max_price_per_hour": 0.1,
                "sort_by": "Price",
                "sort_order": "Ascending",
                "page_num": 0
            }
        }
    }
    
    # Test direct MCP processing
    response = process_mcp_request(request)
    print("Tools Call Response (Direct MCP):")
    print(json.dumps(response, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test HTTP Lambda handler
    http_event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": json.dumps(request)
    }
    
    http_response = lambda_handler(http_event, None)
    print("Tools Call Response (HTTP Lambda):")
    print(json.dumps(http_response, indent=2))
    print("\n" + "="*50 + "\n")

def test_ping():
    """Test the ping request"""
    request = {
        "jsonrpc": "2.0",
        "id": "ping-123",
        "method": "ping"
    }
    
    # Test direct MCP processing
    response = process_mcp_request(request)
    print("Ping Response (Direct MCP):")
    print(json.dumps(response, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test HTTP Lambda handler
    http_event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": json.dumps(request)
    }
    
    http_response = lambda_handler(http_event, None)
    print("Ping Response (HTTP Lambda):")
    print(json.dumps(http_response, indent=2))
    print("\n" + "="*50 + "\n")

def test_error_handling():
    """Test error handling with invalid request"""
    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "nonexistent_method",
        "params": {}
    }
    
    # Test direct MCP processing
    response = process_mcp_request(request)
    print("Error Handling Response (Direct MCP):")
    print(json.dumps(response, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test HTTP Lambda handler
    http_event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": json.dumps(request)
    }
    
    http_response = lambda_handler(http_event, None)
    print("Error Handling Response (HTTP Lambda):")
    print(json.dumps(http_response, indent=2))
    print("\n" + "="*50 + "\n")

def test_cors_preflight():
    """Test CORS preflight request"""
    http_event = {
        "requestContext": {
            "http": {
                "method": "OPTIONS"
            }
        }
    }
    
    http_response = lambda_handler(http_event, None)
    print("CORS Preflight Response:")
    print(json.dumps(http_response, indent=2))
    print("\n" + "="*50 + "\n")

def test_invalid_json():
    """Test handling of invalid JSON"""
    http_event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": "invalid json"
    }
    
    http_response = lambda_handler(http_event, None)
    print("Invalid JSON Response:")
    print(json.dumps(http_response, indent=2))
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    print("Testing AWS Pricing MCP Lambda Handler")
    print("="*50)
    
    try:
        test_initialize()
        test_tools_list()
        test_tools_call()
        test_ping()
        test_error_handling()
        test_cors_preflight()
        test_invalid_json()
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc() 