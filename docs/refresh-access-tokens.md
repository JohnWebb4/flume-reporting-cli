Refresh Access Token

Fetch the complete documentation index at: https://flumetech.readme.io/llms.txt. Use this file to discover all available pages before exploring further. Append .md to any documentation page URL to get its markdown version.

# Refresh Access Token

Refreshes an access token. To retrieve the `user_id`, the JWT token needs to be decoded. The "Content-Type" header must be set to "application/json".

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
    "/oauth/token": {
      "post": {
        "summary": "Refresh Access Token",
        "description": "Refreshes an access token. To retrieve the `user_id`, the JWT token needs to be decoded. The \"Content-Type\" header must be set to \"application/json\".",
        "operationId": "refresh-access-token",
        "parameters": [
          {
            "name": "envelope",
            "in": "query",
            "description": "Whether to envelope the token response in Flume's custom formatting.",
            "schema": {
              "type": "boolean",
              "default": true
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": [
                  "grant_type",
                  "refresh_token",
                  "client_id",
                  "client_secret"
                ],
                "properties": {
                  "grant_type": {
                    "type": "string",
                    "description": "Must be \"refresh_token\".",
                    "default": "refresh_token"
                  },
                  "refresh_token": {
                    "type": "string",
                    "description": "The refresh token used to get a new access token."
                  },
                  "client_id": {
                    "type": "string",
                    "description": "Client ID provided by Flume."
                  },
                  "client_secret": {
                    "type": "string",
                    "description": "Client secret provided by Flume."
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "200",
            "content": {
              "application/json": {
                "examples": {
                  "Result": {
                    "value": "{\n  \"success\": true,\n  \"code\": 602,\n  \"message\": \"Request OK\",\n  \"http_code\": 200,\n  \"http_message\": \"OK\",\n  \"detailed\": null,\n  \"data\": [\n    {\n      \"token_type\": \"bearer\",\n      \"access_token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c\",\n      \"expires_in\": 604800,\n      \"refresh_token\": \"fdb8fdbecf1d03ce5e6125c067733c0d51de209c\"\n    }\n  ],\n  \"count\": 1,\n  \"pagination\": null\n}"
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
                          "token_type": {
                            "type": "string",
                            "example": "bearer"
                          },
                          "access_token": {
                            "type": "string",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
                          },
                          "expires_in": {
                            "type": "integer",
                            "example": 604800,
                            "default": 0
                          },
                          "refresh_token": {
                            "type": "string",
                            "example": "fdb8fdbecf1d03ce5e6125c067733c0d51de209c"
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
                    "value": "{\n  \"success\": false,\n  \"message\": \"invalid_client\",\n  \"http_code\": 400,\n  \"http_message\": \"Bad Request\",\n  \"detailed\": [\n    \"Client credentials are invalid\"\n  ],\n  \"data\": [],\n  \"count\": 0,\n  \"pagination\": null\n}"
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
                      "example": "invalid_client"
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
                        "example": "Client credentials are invalid"
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
          }
        },
        "deprecated": false,
        "security": []
      }
    }
  },
  "x-readme": {
    "headers": [],
    "explorer-enabled": true,
    "proxy-enabled": true
  },
  "x-readme-fauxas": true,
  "_id": "58b53c791065f9c438aa20c3:58123757bb6a680f00f3c29b"
}
```
