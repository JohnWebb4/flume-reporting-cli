Get Current Flow Rate

Fetch the complete documentation index at: https://flumetech.readme.io/llms.txt. Use this file to discover all available pages before exploring further. Append .md to any documentation page URL to get its markdown version.

# Get Current Flow Rate

Check whether water is currently running.

# OpenAPI definition

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Flume API",
    "version": "1.0"
  },
  "servers": [
    {
      "url": "https://api.flumewater.com"
    }
  ],
  "components": {
    "securitySchemes": {
      "sec0": {
        "type": "oauth2",
        "flows": {
          "clientCredentials": {
            "tokenUrl": "https://example.com/oauth2/token",
            "scopes": {}
          }
        }
      }
    }
  },
  "security": [
    {
      "sec0": []
    }
  ],
  "paths": {
    "/users/{user_id}/devices/{device_id}/query/active": {
      "get": {
        "summary": "Get Current Flow Rate",
        "description": "Check whether water is currently running.",
        "operationId": "get-current-flow-rate",
        "parameters": [
          {
            "name": "user_id",
            "in": "path",
            "description": "ID of the user",
            "schema": {
              "type": "integer",
              "format": "int32"
            },
            "required": true
          },
          {
            "name": "device_id",
            "in": "path",
            "description": "ID of the device",
            "schema": {
              "type": "string"
            },
            "required": true
          }
        ],
        "responses": {
          "200": {
            "description": "200",
            "content": {
              "application/json": {
                "examples": {
                  "Result": {
                    "value": "{\n    \"success\": true,\n    \"code\": 602,\n    \"message\": \"Request OK\",\n    \"http_code\": 200,\n    \"http_message\": \"OK\",\n    \"detailed\": null,\n    \"data\": [\n        {\n            \"active\": true,\n            \"gpm\": 0.78,\n            \"datetime\": \"2024-01-01 15:22:00\"\n        }\n    ],\n    \"count\": 1,\n    \"pagination\": null\n}"
                  }
                },
                "schema": {
                  "type": "object",
                  "properties": {
                    "success": {
                      "type": "boolean",
                      "example": true,
                      "default": true
                    },
                    "code": {
                      "type": "integer",
                      "example": 602,
                      "default": 0
                    },
                    "message": {
                      "type": "string",
                      "example": "Request OK"
                    },
                    "http_code": {
                      "type": "integer",
                      "example": 200,
                      "default": 0
                    },
                    "http_message": {
                      "type": "string",
                      "example": "OK"
                    },
                    "detailed": {},
                    "data": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "active": {
                            "type": "boolean",
                            "example": true,
                            "default": true
                          },
                          "gpm": {
                            "type": "number",
                            "example": 0.78,
                            "default": 0
                          },
                          "datetime": {
                            "type": "string",
                            "example": "2024-01-01 15:22:00"
                          }
                        }
                      }
                    },
                    "count": {
                      "type": "integer",
                      "example": 1,
                      "default": 0
                    },
                    "pagination": {}
                  }
                }
              }
            }
          },
          "404": {
            "description": "404",
            "content": {
              "application/json": {
                "examples": {
                  "Result": {
                    "value": "{\n  \"success\": false,\n  \"code\": 610,\n  \"message\": \"Record could not be found\",\n  \"http_code\": 404,\n  \"http_message\": \"Not Found\",\n  \"detailed\": null,\n  \"data\": [],\n  \"count\": 0,\n  \"pagination\": null\n}"
                  }
                },
                "schema": {
                  "type": "object",
                  "properties": {
                    "success": {
                      "type": "boolean",
                      "example": false,
                      "default": true
                    },
                    "code": {
                      "type": "integer",
                      "example": 610,
                      "default": 0
                    },
                    "message": {
                      "type": "string",
                      "example": "Record could not be found"
                    },
                    "http_code": {
                      "type": "integer",
                      "example": 404,
                      "default": 0
                    },
                    "http_message": {
                      "type": "string",
                      "example": "Not Found"
                    },
                    "detailed": {},
                    "data": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {}
                      }
                    },
                    "count": {
                      "type": "integer",
                      "example": 0,
                      "default": 0
                    },
                    "pagination": {}
                  }
                }
              }
            }
          }
        },
        "deprecated": false
      }
    }
  },
  "x-readme": {
    "headers": [],
    "explorer-enabled": true,
    "proxy-enabled": true
  },
  "x-readme-fauxas": true,
  "_id": "58b70615b72a430f007f9f99:66a08e6729b2a400196d3e39"
}
```
