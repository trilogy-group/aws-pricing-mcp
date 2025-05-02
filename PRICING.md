## Pricing Data JSON Format

The pricing data JSON file has the following structure:

```json
{
  "instance_family_name": {
    "Current Generation": "Yes/No",
    "Instance Family": "General Purpose/Compute Optimized/etc.",
    "Physical Processor": "Intel Xeon/AMD EPYC/etc.",
    "Clock Speed": 2.5,
    "Processor Features": "AVX, AVX2, etc.",
    "Enhanced Networking Supported": "Yes/No",
    "sizes": {
      "instance_size": {
        "vCPU": 2,
        "Memory": 8.0,
        "Ephemeral Storage": 0,
        "Network Performance": 5000,
        "Dedicated EBS Throughput": 650,
        "GPU": 0,
        "GPU Memory": 0,
        "operations": {
          "operation_code": {
            "region": "price1,price2,price3,..."
          }
        }
      }
    }
  }
}
```

### Field Descriptions

#### Instance Family Level Fields

- **Instance Family Name**: The name of the instance family (e.g., "t3a")
- **Current Generation**: Indicates if the instance family is current generation ("Yes") or previous generation ("No")
- **Instance Family**: The AWS classification of the instance family (e.g., "General Purpose", "Compute Optimized")
- **Physical Processor**: The CPU manufacturer and model (e.g., "Intel Xeon Platinum 8175", "AMD EPYC 7R13")
- **Clock Speed**: The processor clock speed in GHz (e.g., 2.5)
- **Processor Features**: Special CPU features or instruction sets (e.g., "AVX, AVX2, Intel AVX-512")
- **Enhanced Networking Supported**: Whether enhanced networking is supported ("Yes" or "No")

#### Instance Size Level Fields

- **Instance Size Name**: The name of the instance size (e.g., "2xlarge")
- **vCPU**: Number of virtual CPUs
- **Memory**: Amount of RAM in GiB
- **Ephemeral Storage**: Amount of instance store storage in GB (0 for EBS-only instances)
- **Network Performance**: Network performance in Mbps
- **Dedicated EBS Throughput**: EBS throughput in Mbps
- **GPU**: Number of GPUs (0 if none)
- **GPU Memory**: Amount of GPU memory in GB (0 if no GPU)

#### Operations and Pricing

The `operations` object contains mappings from operation codes to region-specific pricing. Each region has a comma-separated string of prices with the following positions:

- Position 0: OnDemand price for Shared tenancy
- Position 1: No Upfront 1yr Compute Savings Plan price for Shared tenancy
- Position 2: Partial Upfront 1yr Compute Savings Plan price for Shared tenancy
- Position 3: All Upfront 1yr Compute Savings Plan price for Shared tenancy
- Position 4: No Upfront 3yr Compute Savings Plan price for Shared tenancy
- Position 5: Partial Upfront 3yr Compute Savings Plan price for Shared tenancy
- Position 6: All Upfront 3yr Compute Savings Plan price for Shared tenancy
- Position 7: OnDemand price for Dedicated tenancy
- Position 8: No Upfront 1yr Compute Savings Plan price for Dedicated tenancy
- Position 9: Partial Upfront 1yr Compute Savings Plan price for Dedicated tenancy
- Position 10: All Upfront 1yr Compute Savings Plan price for Dedicated tenancy
- Position 11: No Upfront 3yr Compute Savings Plan price for Dedicated tenancy
- Position 12: Partial Upfront 3yr Compute Savings Plan price for Dedicated tenancy
- Position 13: All Upfront 3yr Compute Savings Plan price for Dedicated tenancy

Empty string values indicate that no pricing is available for that specific combination.

## Operation System to Operation Code Mapping

The following table shows the mapping between operating systems and their corresponding operation codes:

| Operating System | Operation Code |
|------------------|---------------|
| Linux/UNIX | "" (empty string) |
| Red Hat BYOL Linux | "00g0" |
| Red Hat Enterprise Linux | "0010" |
| Red Hat Enterprise Linux with HA | "1010" |
| Red Hat Enterprise Linux with SQL Server Standard and HA | "1014" |
| Red Hat Enterprise Linux with SQL Server Enterprise and HA | "1110" |
| Red Hat Enterprise Linux with SQL Server Standard | "0014" |
| Red Hat Enterprise Linux with SQL Server Web | "0210" |
| Red Hat Enterprise Linux with SQL Server Enterprise | "0110" |
| Linux with SQL Server Enterprise | "0100" |
| Linux with SQL Server Standard | "0004" |
| Linux with SQL Server Web | "0200" |
| SUSE Linux | "000g" |
| Windows | "0002" |
| Windows BYOL | "0800" |
| Windows with SQL Server Enterprise | "0102" |
| Windows with SQL Server Standard | "0006" |
| Windows with SQL Server Web | "0202" |
