This document provides example JSON-RPC messages for the supported MCP commands.

# Example JSON-RPC Messages for Anthropic MCP (Stateless HTTP Mode)

Below are example JSON-RPC 2.0 request and response objects for each relevant Model Context Protocol (MCP) command in stateless HTTP mode. Each example shows a complete JSON structure with realistic field values, based on the MCP specification. (All streaming or SSE-based fields are omitted, as these examples assume a non-streaming HTTP interaction.)

## initialize

**Description:** The client begins a session by sending an `initialize` request with its supported protocol version, capabilities, and client info. The server replies with its own protocol version (which may be negotiated), supported server capabilities (e.g. logging, prompts, resources, tools), server info, and any optional instructions.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "roots": {
        "listChanged": true
      },
      "sampling": {}
    },
    "clientInfo": {
      "name": "ExampleClient",
      "version": "1.0.0"
    }
  }
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "logging": {},
      "prompts": {
        "listChanged": true
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      },
      "tools": {
        "listChanged": true
      }
    },
    "serverInfo": {
      "name": "ExampleServer",
      "version": "1.0.0"
    },
    "instructions": "Optional instructions for the client"
  }
}
```



## initialized (notification)

**Description:** After the server responds to `initialize`, the client sends an `initialized` notification to signal that it is ready for normal operations. This is a JSON-RPC notification (no `id` field and no response expected).

**Notification:**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```



## ping

**Description:** Either party can send a `ping` request at any time to check connectivity. The `ping` request has no parameters, and the receiver must promptly return an empty result object if still alive.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "method": "ping"
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "result": {}
}
```



## resources/list

**Description:** The client requests a list of available resources (files, data, etc.) from the server. The `resources/list` request may include an optional `cursor` for pagination. The response contains an array of resource descriptors (each with fields like `uri`, `name`, `description`, `mimeType`, etc.) and may include a `nextCursor` token if more results are available.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/list",
  "params": {
    "cursor": "optional-cursor-value"
  }
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resources": [
      {
        "uri": "file:///project/src/main.rs",
        "name": "main.rs",
        "description": "Primary application entry point",
        "mimeType": "text/x-rust"
      }
    ],
    "nextCursor": "next-page-cursor"
  }
}
```



## resources/read

**Description:** The client retrieves the contents of a specific resource by sending `resources/read` with the resource's URI. The server's response includes a `contents` array with the resource data. If the resource is text-based, it appears under a `text` field (with an associated MIME type); for binary data, a `blob` (base64 string) would be used instead.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "resources/read",
  "params": {
    "uri": "file:///project/src/main.rs"
  }
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "contents": [
      {
        "uri": "file:///project/src/main.rs",
        "mimeType": "text/x-rust",
        "text": "fn main() {\n    println!(\"Hello world!\");\n}"
      }
    ]
  }
}
```



## resources/templates/list

**Description:** The client can query available *resource templates* (parameterized resource URIs) by sending `resources/templates/list`. The response provides a list of resource template definitions, each with a `uriTemplate` (often containing placeholders), a human-readable `name` and `description`, and an optional `mimeType` indicating the type of resource produced.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "resources/templates/list"
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "resourceTemplates": [
      {
        "uriTemplate": "file:///{path}",
        "name": "Project Files",
        "description": "Access files in the project directory",
        "mimeType": "application/octet-stream"
      }
    ]
  }
}
```



## prompts/list

**Description:** The client requests a list of available prompt templates by sending `prompts/list`. This may also support pagination via a `cursor`. The server responds with an array of prompt definitions, where each prompt has a unique `name`, a `description` of what it does, and an optional list of expected `arguments` (each argument with a name, description, and whether it's required). A `nextCursor` may be provided if the list is paginated.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "prompts/list",
  "params": {
    "cursor": "optional-cursor-value"
  }
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "prompts": [
      {
        "name": "code_review",
        "description": "Asks the LLM to analyze code quality and suggest improvements",
        "arguments": [
          {
            "name": "code",
            "description": "The code to review",
            "required": true
          }
        ]
      }
    ],
    "nextCursor": "next-page-cursor"
  }
}
```



## prompts/get

**Description:** To fetch the content of a specific prompt template (possibly filling in arguments), the client sends `prompts/get` with the prompt's `name` and an `arguments` object providing any required values. The server returns the resolved prompt: typically a `description` and a sequence of `messages` that make up the prompt. Each message has a `role` (e.g. "user" or "assistant") and `content` which could be text or other supported content types.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "code": "def hello():\n    print('world')"
    }
  }
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "description": "Code review prompt",
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Please review this Python code:\n def hello():\n    print('world')"
        }
      }
    ]
  }
}
```



## tools/list

**Description:** The client sends `tools/list` to get the list of tools (functions/actions) the server provides. The response includes an array of tool definitions. Each tool has a `name`, a `description` of its functionality, and an `inputSchema` (a JSON Schema object) describing the expected parameters for that tool. The example below shows one tool with a required `location` parameter. A `nextCursor` may appear if the list is paginated.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {
    "cursor": "optional-cursor-value"
  }
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather information for a location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name or zip code"
            }
          },
          "required": ["location"]
        }
      }
    ],
    "nextCursor": "next-page-cursor"
  }
}
```



## tools/call

**Description:** To execute a specific tool, the client sends a `tools/call` request with the tool's `name` and an `arguments` object providing the needed inputs. The server will run the tool and return a result. The result includes a `content` array (which may contain text or other content types, depending on what the tool returns) and an `isError` boolean indicating whether the tool succeeded. In this example, the tool returns a text result (weather information) and `isError: false` to show success.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "New York"
    }
  }
}
```



**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Current weather in New York:\n Temperature: 72°F\n Conditions: Partly cloudy"
      }
    ],
    "isError": false
  }
}
```



## notifications/cancelled (notification)

**Description:** If either side needs to cancel an in-progress request (e.g. due to a timeout or user action), it sends a `notifications/cancelled` notification. This one-way message includes the `requestId` of the original request to be aborted and an optional `reason` string. The receiver should stop work on that request but does not send any response to the notification.

**Notification:**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/cancelled",
  "params": {
    "requestId": "123",
    "reason": "User requested cancellation"
  }
}
```



Each JSON example above illustrates the structure and fields defined by the MCP specification for stateless HTTP usage, covering the full request/response cycle (or one-way notification) for that command. These messages can be sent over an HTTP-based JSON-RPC connection to manage the model's context and actions without using server-sent events or streaming protocols. All field names and nesting conform to the MCP spec, ensuring interoperability between MCP clients and servers.


## Introduction

This specification aims to describe a simple protocol for LLMs to discover and use remote APIs, while minimizing the context window used. While Anthropic's Model Context Protocol (MCP) is primarily used for the purpose, its design is non-optimal. MCP began as a simple STDIO‑based local solution but evolved into a complex, stateful HTTP/SSE system that burdens developers with session management and infrastructure headaches. Maintaining persistent connections conflicts with stateless microservice patterns, leading to scalability and load‑balancing challenges. This specification adopts a minimal, stateless design to avoid these pitfalls.

## Overview

Webtools expose a lightweight, HTTP‑based contract that allows consumers to

* **Discover** capabilities through self‑describing metadata
* **Validate** inputs and outputs via JSON Schema definitions
  * one schema for the request object (`requestSchema`)
  * one schema for the response object (`responseSchema`)
* **Execute** actions with optional per‑request configuration
* **Consume** predictable, strongly‑typed responses
* **Lock-in** specific API versions to improve security

## Use Case Scenario

Webtools are defined by URLs. The typical workflow follows these steps:

1. **Discovery**: A user finds a webtool URL from a tool provider, marketplace, or other source
2. **Metadata Retrieval**: The user's system issues a GET request to the URL to retrieve the webtool's metadata
3. **Configuration**: The user fills in configuration data according to the `configSchema` defined in the metadata
4. **Integration**: The system is now able to use the webtool with LLMs, passing the configuration and handling requests/responses

### Security Considerations

After reviewing the schemas and metadata, users may choose to lock-in a specific version by storing the validated metadata on their side and no longer fetching it from the remote server. This prevents potential security risks where malicious instructions could be injected into the LLM context through schema changes in newer versions of the webtool metadata.

## HTTP Methods

### GET {webtoolUrl}/ — Webtool Metadata (latest)

Returns metadata about the **latest** version of the webtool.

```json
{
  "name": "webtool_name",
  "description": "Human‑readable description of what this webtool does",
  "version": "2.1.0",
  "actions": [
    {
      "name": "action_name",
      "description": "What this action does",
      "requestSchema": { /* JSON Schema for request */ },
      "responseSchema": { /* JSON Schema for response */ }
    }
  ],
  "configSchema": { /* JSON Schema for configuration */ },
  "defaultConfig": { /* Default configuration values */ }
}
```

### GET {webtoolUrl}/{version} — Webtool Metadata (specific version)

Returns metadata **for the specified semantic version**. Use this to fetch historical versions or pin a client to a stable release. The `version` parameter is optional; if omitted, the server SHOULD default to the latest version.

```http
GET /1.0.0
```

```json
{
  "name": "weather",
  "description": "Provides weather information",
  "version": "1.0.0",
  "actions": [ /* …as above… */ ],
  "configSchema": { /* … */ },
  "defaultConfig": { /* … */ }
}
```

> **Note**: If the version is not found, the endpoint should return `404 Not Found` with an error envelope identical to the standard error response.

### POST {webtoolUrl}/ — Webtool Execution

```json
{
  "sessionId": "unique-session-identifier",
  "version": "1.0.0",
  "action": "action_name",
  "config": { /* Optional configuration object matching configSchema */ },
  "request": { /* Required data matching requestSchema */ }
}
```

The `sessionId` field is optional and used for maintaining state across multiple requests to the same webtool. The `version` field is optional; if omitted, the server SHOULD default to the latest version. The `config` property contains data that is not generated by the LLM but rather supplied by the environment, allowing minimization of context use, passing security credentials, parameter defaults, or user-configured values.

#### Response Examples

##### Successful Response

```json
{
  "status": "ok",
  "data": { /* Action‑specific result */ }
}
```

##### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_INPUT",
    "message": "Validation failed for field 'location'"
  }
}
```

## Content Types

All requests and responses MUST use `application/json` content type. Servers MUST include `Content-Type: application/json` headers in their responses.

## JSON Schema Requirements

Webtools MAY use any JSON Schema features. Schemas SHOULD include descriptions and example values to help LLMs understand the expected data structure and format.

## Error Handling

The specification defines standard error codes for common validation errors:
- `WEBTOOL_NOT_FOUND` - Requested webtool or version does not exist
- `SCHEMA_ERROR` - Request data does not match the action's requestSchema
- `CONFIG_ERROR` - Configuration data does not match the webtool's configSchema
- `RATE_LIMIT` - Request rate limit exceeded
- `INTERNAL_ERROR` - Unrecoverable server error

Webtools MAY define their own custom error codes for domain-specific errors. Error messages SHOULD be human-readable.

## Integration Guides

### Using Webtools with the **Vercel AI SDK**

The Vercel AI SDK supports OpenAI‑style *tool calling* out‑of‑the‑box.

#### 1 – Fetch Metadata at Build Time

```ts
// lib/tools/weather.ts
import type { Tool } from "ai";

export async function getWeatherTool(): Promise<Tool> {
  const res = await fetch("/api/webtools/weather");
  const meta = await res.json();
  return {
    name: meta.name,
    description: meta.description,
    parameters: meta.actions[0].requestSchema, // <-- uses requestSchema
    execute: async (args) => {
      const exec = await fetch("/api/webtools/weather", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          sessionId: crypto.randomUUID(),
          action: args.action,
          request: args
        })
      });
      return (await exec.json()).data; // unwrap the envelope
    }
  };
}
```

#### 2 – Create a Tool Caller

```ts
import { createToolCaller } from "ai/tool-caller";
import OpenAI from "@ai-sdk/openai";
import { getWeatherTool } from "@/lib/tools/weather";

const toolCaller = createToolCaller([await getWeatherTool()]);

export async function chat(messages) {
  const llm = new OpenAI();
  const modelResponse = await llm.chat({ messages, tools: toolCaller.tools });
  const final = await toolCaller.call(modelResponse);
  return final;
}
```

> **Tip:** The AI SDK automatically translates `requestSchema` into the function‑calling format the model expects.

### Using Webtools with **LangChain**

LangChain's `StructuredTool` helper lets you wrap a webtool with schema metadata so agents can invoke it.

```python
from langchain_core.tools import StructuredTool
import requests, uuid

WEATHER_ENDPOINT = "https://api.example.com/webtools/weather"

def run_get_current(location: str, units: str = "metric"):
    body = {
        "sessionId": str(uuid.uuid4()),
        "action": "get_current",
        "request": {"location": location},
        "config": {"units": units}
    }
    return requests.post(WEATHER_ENDPOINT, json=body, timeout=10).json()

weather_tool = StructuredTool.from_function(
    func=run_get_current,
    name="get_current_weather",
    description="Return the current weather for a given location via the Weather webtool",
    schema={
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}
        },
        "required": ["location"]
    }
)
```

Then add `weather_tool` to any LCEL runnable or agent:

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent

llm = ChatOpenAI(model_name="gpt-4o")
agent = create_openai_functions_agent(llm, tools=[weather_tool])
executor = AgentExecutor(agent=agent, tools=[weather_tool])

result = executor.invoke("Should I take an umbrella to Paris today?")
print(result)
```

## Error Handling & Best Practices

* Validate client input against each action's `requestSchema` before issuing a POST.
* For recoverable failures (4xx), return `status: "error"` with appropriate error codes.
* For unrecoverable server errors (5xx), set code `INTERNAL_ERROR` and avoid leaking internals.
* Use standard HTTP status codes alongside the JSON response for broad compatibility.
* Rate limiting, quotas, and other implementation details are left to implementers.

## Authentication & Authorization

This specification is agnostic regarding authorization schemes. Consumers MAY include an Authorization: Bearer <token> header on every request. Additional details—such as token scopes, expiration, or refresh flows—are considered implementation-specific and are not mandated by this spec.

---

**Version:** 2025‑06‑30
