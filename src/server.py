"""
AWS Pricing MCP Server

This server exposes AWS EC2 instance pricing data through the Model Context Protocol (MCP).
It provides tools to find the cheapest EC2 instances based on specified criteria.
"""

import json
import os
import sys
import traceback
from typing import List, Dict, Any
from fastmcp import FastMCP, Context

# Set up error logging
def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)

# Load pricing data
try:
    PRICING_FILE = os.path.join(os.path.dirname(__file__), "ec2_pricing.json") 
    if not os.path.exists(PRICING_FILE):
        log_error(f"Pricing file not found at {PRICING_FILE}")
        raise FileNotFoundError(f"Could not find ec2_pricing.json")
    
    with open(PRICING_FILE, "r") as f:
        PRICING_DATA = json.load(f)
        
except Exception as e:
    log_error(f"Failed to load pricing data: {str(e)}")
    log_error(traceback.format_exc())
    raise

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

# Create an MCP server
mcp = FastMCP("AWS EC2 Pricing MCP", log_level="ERROR")

# Define Tools
@mcp.tool()
def find_instances(
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
    filter_max_price_per_hour: float = float('inf'),
    filter_family: str = "",
    filter_size: str = "",
    filter_processor: str = "",
    sort_by: str = "Price",
    sort_order: str = "Descending",
    page_num: int = 0
) -> List[Dict[str, Any]]:
    """
    Find AWS EC2 instances based on specified criteria.
    
    Filter Parameters:
    - region: AWS region (default: us-east-1)
    - platform: OS platform (one of: Linux/UNIX, Red Hat Enterprise Linux, Red Hat Enterprise Linux with HA, Red Hat Enterprise Linux with SQL Server Standard and HA, Red Hat Enterprise Linux with SQL Server Enterprise and HA, Red Hat Enterprise Linux with SQL Server Standard, Red Hat Enterprise Linux with SQL Server Web, Linux with SQL Server Enterprise, Linux with SQL Server Standard, Linux with SQL Server Web, SUSE Linux, Windows, Windows BYOL, Windows with SQL Server Enterprise, Windows with SQL Server Standard, Windows with SQL Server Web; default: Linux/UNIX)
    - tenancy: Instance tenancy (one of: Shared, Dedicated; default: Shared)
    - pricing_model: Pricing model (one of: On Demand, 1-yr No Upfront, 1-yr Partial Upfront, 1-yr All Upfront, 3-yr No Upfront, 3-yr Partial Upfront, 3-yr All Upfront; default: On Demand)
    - min_vcpu: Minimum number of vCPUs (default: 0)
    - min_ram: Minimum amount of RAM in GB (default: 0)
    - min_gpu: Minimum number of GPUs (default: 0)
    - min_gpu_memory: Minimum GPU memory in GB (default: 0)
    - min_cpu_ghz: Minimum CPU clock speed in GHz (default: 0)
    - min_network_performance: Minimum network performance in Mbps (default: 0)
    - min_ebs_throughput: Minimum dedicated EBS throughput in Mbps (default: 0)
    - min_ephemeral_storage: Minimum ephemeral storage in GB (default: 0)
    - max_price_per_hour: Maximum price per hour in USD (default: no limit)
    - sort_by: Field to sort by (one of: Price, Clock Speed GHz, vCPU cores, Memory GB, Ephemeral Storage GB, Network Performance Mbps, Dedicated EBS Throughput Mbps, GPU cores, GPU Memory GB; default: Price)
    - sort_order: Sort order (one of: Ascending, Descending; default: Descending)
    - family: Filter by instance family (e.g., "m5", "c6g"; default: "" for all families)
    - size: Filter by instance size (e.g., "large", "2xlarge"; default: "" for all sizes)
    - processor: Filter by physical processor (e.g., "Graviton", "Xeon", "AMD"; default: "" for all processors)
    - page_num: Page number for pagination (default: 0)
    
    Returns:
    - List of instances matching the criteria (5 per page). CloudFix RightSpend pricing is provided when using the flexible cRIs provided by RightSpend (a third-party solution). The benefit of RightSpend is that it 1) eliminates the need for complex forecasting or frequent consultations with engineering about usage fluctuations 2) removes the risk of unused reservations 3) provides 3-yr All Upfront discounts without the need for prepayment.
 
    """
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
    if filter_max_price_per_hour != float('inf'):
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

# Run the server if executed directly
if __name__ == "__main__":
    # res = find_instances()
    # print(res)
    mcp.run(transport="stdio")
