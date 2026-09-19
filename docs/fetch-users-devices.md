Fetch User's Devices

Fetch the complete documentation index at: https://flumetech.readme.io/llms.txt. Use this file to discover all available pages before exploring further. Append .md to any documentation page URL to get its markdown version.

# Fetch User's Devices

Returns the devices associated with a user.

Bridge devices have `type=1`. Sensor devices have `type=2`.

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
    "/users/{user_id}/devices": {
      "get": {
        "summary": "Fetch User's Devices",
        "description": "Returns the devices associated with a user.\n\nBridge devices have `type=1`. Sensor devices have `type=2`.",
        "operationId": "get-a-users-devices",
        "parameters": [
          {
            "name": "user_id",
            "in": "path",
            "description": "ID of the user",
            "required": true,
            "schema": {
              "type": "integer",
              "format": "int32"
            }
          },
          {
            "name": "limit",
            "in": "query",
            "description": "How many devices to return",
            "schema": {
              "type": "integer",
              "format": "int32",
              "default": 50
            }
          },
          {
            "name": "offset",
            "in": "query",
            "description": "Offset of devices to return",
            "schema": {
              "type": "integer",
              "format": "int32",
              "default": 0
            }
          },
          {
            "name": "sort_field",
            "in": "query",
            "description": "Which field to sort devices on",
            "schema": {
              "type": "string",
              "default": "id"
            }
          },
          {
            "name": "sort_direction",
            "in": "query",
            "description": "Which direction to sort devices on",
            "schema": {
              "type": "string",
              "default": "ASC"
            }
          },
          {
            "name": "user",
            "in": "query",
            "description": "Include user data in response",
            "schema": {
              "type": "boolean",
              "default": false
            }
          },
          {
            "name": "location",
            "in": "query",
            "description": "Include location data in response",
            "schema": {
              "type": "boolean",
              "default": false
            }
          },
          {
            "name": "list_shared",
            "in": "query",
            "description": "Determines whether to include devices that have granted shared access to user",
            "schema": {
              "type": "boolean",
              "default": false
            }
          },
          {
            "name": "primary_location",
            "in": "query",
            "description": "Only include devices associated to a primary location if true. Exclude devices associated to a primary location if false.",
            "schema": {
              "type": "boolean"
            }
          },
          {
            "name": "location_id",
            "in": "query",
            "description": "Find devices associated to a specified location ID",
            "schema": {
              "type": "integer",
              "format": "int32"
            }
          },
          {
            "name": "type",
            "in": "query",
            "description": "Filter devices by their type (Bridge: 1, Water Sensor: 2)",
            "schema": {
              "type": "integer",
              "format": "int32"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "200",
            "content": {
              "application/json": {
                "examples": {
                  "Result": {
                    "value": "{\n  \"success\": true,\n  \"code\": 602,\n  \"message\": \"Request OK\",\n  \"http_code\": 200,\n  \"http_message\": \"OK\",\n  \"detailed\": null,\n  \"data\": [\n    {\n      \"id\": \"6721255604737738501\",\n      \"type\": 2,\n      \"location_id\": 44565,\n      \"user_id\": 1682,\n      \"bridge_id\": \"6782193059647718740\",\n      \"oriented\": true,\n      \"last_seen\": \"2021-12-29T05:47:34.000Z\",\n      \"connected\": true,\n      \"battery_level\": \"medium\",\n      \"product\": \"flume2\"\n    }\n  ],\n  \"count\": 1,\n  \"pagination\": null\n}"
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
                          "id": {
                            "type": "string",
                            "example": "6721255604737738501"
                          },
                          "type": {
                            "type": "integer",
                            "example": 2,
                            "default": 0
                          },
                          "location_id": {
                            "type": "integer",
                            "example": 44565,
                            "default": 0
                          },
                          "user_id": {
                            "type": "integer",
                            "example": 1682,
                            "default": 0
                          },
                          "bridge_id": {
                            "type": "string",
                            "example": "6782193059647718740"
                          },
                          "oriented": {
                            "type": "boolean",
                            "example": true,
                            "default": true
                          },
                          "last_seen": {
                            "type": "string",
                            "example": "2021-12-29T05:47:34.000Z"
                          },
                          "connected": {
                            "type": "boolean",
                            "example": true,
                            "default": true
                          },
                          "battery_level": {
                            "type": "string",
                            "example": "medium"
                          },
                          "product": {
                            "type": "string",
                            "example": "flume2"
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
  "_id": "58b70615b72a430f007f9f99:57feff2104982c0e00caa91e"
}
```
