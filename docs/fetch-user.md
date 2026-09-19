Fetch User

Fetch the complete documentation index at: https://flumetech.readme.io/llms.txt. Use this file to discover all available pages before exploring further. Append .md to any documentation page URL to get its markdown version.

# Fetch User

Returns a single Flume user.

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
    "/users/{user_id}": {
      "get": {
        "summary": "Fetch User",
        "description": "Returns a single Flume user.",
        "operationId": "fetch-single-user",
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
          }
        ],
        "responses": {
          "200": {
            "description": "200",
            "content": {
              "application/json": {
                "examples": {
                  "Result": {
                    "value": "{\n  \"success\": true,\n  \"code\": 602,\n  \"message\": \"Request OK\",\n  \"http_code\": 200,\n  \"http_message\": \"OK\",\n  \"detailed\": null,\n  \"data\": [\n    {\n      \"id\": 10000,\n      \"email_address\": \"user@example.com\",\n      \"first_name\": \"Flume\",\n      \"last_name\": \"Tech\",\n      \"phone\": \"1111111111\",\n      \"status\": \"Active\",\n      \"type\": \"USER\"\n    }\n  ],\n  \"count\": 1,\n  \"pagination\": null\n}"
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
                            "type": "integer",
                            "example": 10000,
                            "default": 0
                          },
                          "email_address": {
                            "type": "string",
                            "example": "user@example.com"
                          },
                          "first_name": {
                            "type": "string",
                            "example": "Flume"
                          },
                          "last_name": {
                            "type": "string",
                            "example": "Tech"
                          },
                          "phone": {
                            "type": "string",
                            "example": "1111111111"
                          },
                          "status": {
                            "type": "string",
                            "example": "Active"
                          },
                          "type": {
                            "type": "string",
                            "example": "USER"
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
          "400": {
            "description": "400",
            "content": {
              "application/json": {
                "examples": {
                  "Result": {
                    "value": "{\n  \"success\": false,\n  \"message\": \"invalid_request\",\n  \"http_code\": 400,\n  \"http_message\": \"Bad Request\",\n  \"detailed\": [\n    \"The access token was not found\"\n  ],\n  \"data\": [],\n  \"count\": 0,\n  \"pagination\": null\n}"
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
                    "message": {
                      "type": "string",
                      "example": "invalid_request"
                    },
                    "http_code": {
                      "type": "integer",
                      "example": 400,
                      "default": 0
                    },
                    "http_message": {
                      "type": "string",
                      "example": "Bad Request"
                    },
                    "detailed": {
                      "type": "array",
                      "items": {
                        "type": "string",
                        "example": "The access token was not found"
                      }
                    },
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
  "_id": "58b70615b72a430f007f9f99:57fc16634002550e004c0376"
}
```
