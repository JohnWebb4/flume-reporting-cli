Query a User's Device

Fetch the complete documentation index at: https://flumetech.readme.io/llms.txt. Use this file to discover all available pages before exploring further. Append .md to any documentation page URL to get its markdown version.

# Query a User's Device

Ask a device questions about its water usage. See [Querying Samples](https://flumetech.readme.io/v1.0/docs/querying-samples) for detailed info. The "Content-Type" header must be set to "application/json".

Example Query:

[block:code]
{
  "codes": [
    {
      "code": "{\n\t\"queries\": [\n\t\t{\n\t\t\t\"request_id\": \"abc\",\n\t\t\t\"bucket\": \"MON\",\n\t\t\t\"since_datetime\": \"2016-04-04 01:00:00\",\n\t\t\t\"group_multiplier\": 3\n\t\t},\n\t\t{\n\t\t\t\"request_id\": \"xyz\",\n\t\t\t\"bucket\": \"DAY\",\n\t\t\t\"since_datetime\": \"2016-04-04 01:00:00\",\n\t\t\t\"until_datetime\": \"2016-04-07 01:00:00\"\n\t\t}\n\t]\n}",
      "language": "json"
    }
  ]
}
[/block]

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
    "/users/{user_id}/devices/{device_id}/query": {
      "post": {
        "summary": "Query a User's Device",
        "description": "Ask a device questions about its water usage. See [Querying Samples](https://flumetech.readme.io/v1.0/docs/querying-samples) for detailed info. The \"Content-Type\" header must be set to \"application/json\".",
        "operationId": "query-a-user-device",
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
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": [
                  "queries"
                ],
                "properties": {
                  "queries": {
                    "type": "array",
                    "description": "Array of questions to ask. See [Querying Samples](https://flumetech.readme.io/v1.0/docs/querying-samples) for detailed info",
                    "items": {
                      "properties": {
                        "request_id": {
                          "type": "string",
                          "description": "The ID for this query."
                        },
                        "bucket": {
                          "type": "string",
                          "description": "The bucket size."
                        },
                        "since_datetime": {
                          "type": "string",
                          "description": "Lower time constraint."
                        },
                        "until_datetime": {
                          "type": "string",
                          "description": "Upper time constraint."
                        },
                        "group_multiplier": {
                          "type": "string",
                          "description": "The group multiplier."
                        },
                        "operation": {
                          "type": "string",
                          "description": "The optional type of aggregate/accumulate operation to perform. Options are SUM, AVG, MIN, MAX, CNT"
                        },
                        "sort_direction": {
                          "type": "string",
                          "description": "Ascending and descending supported. Which way to sort the results."
                        },
                        "units": {
                          "type": "string",
                          "description": "The unit of measurement to return the water usage data by. Options are GALLONS, LITERS, CUBIC_FEET, and CUBIC_METERS.",
                          "default": "GALLONS"
                        },
                        "types": {
                          "type": "array",
                          "description": "List of water types to include in the output. The \"all\" type returns total usage using the \"value\" field in each output object. Other values can be found in Water Types, and appear in the \"types\" field in each output object.",
                          "default": [],
                          "items": {
                            "type": "string"
                          }
                        }
                      },
                      "required": [
                        "request_id",
                        "bucket"
                      ],
                      "type": "object"
                    }
                  }
                }
              },
              "examples": {
                "Request Example": {
                  "value": {
                    "queries": [
                      {
                        "request_id": "abc",
                        "bucket": "MON",
                        "since_datetime": "2016-04-04 01:00:00",
                        "group_multiplier": 3
                      },
                      {
                        "request_id": "xyz",
                        "bucket": "DAY",
                        "since_datetime": "2016-04-04 01:00:00",
                        "until_datetime": "2016-04-07 01:00:00"
                      }
                    ]
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
                    "value": "{\n  \"success\": true,\n  \"code\": 602,\n  \"message\": \"Request OK\",\n  \"http_code\": 200,\n  \"http_message\": \"OK\",\n  \"detailed\": null,\n  \"data\": [\n    {\n      \"abc\": [\n        {\n          \"datetime\": \"2016-04-01 00:00:00\",\n          \"value\": 20\n        },\n        {\n          \"datetime\": \"2016-07-01 00:00:00\",\n          \"value\": 35.5\n        },\n        {\n          \"datetime\": \"2016-10-01 00:00:00\",\n          \"value\": 40\n        }\n      ],\n      \"xyz\": [\n        {\n          \"datetime\": \"2016-04-04 00:00:00\",\n          \"value\": 1000\n        },\n        {\n          \"datetime\": \"2016-04-05 00:00:00\",\n          \"value\": 200\n        },\n        {\n          \"datetime\": \"2016-04-06 00:00:00\",\n          \"value\": 21\n        },\n        {\n          \"datetime\": \"2016-04-07 00:00:00\",\n          \"value\": 30\n        }\n      ]\n    }\n  ],\n  \"count\": 0,\n  \"pagination\": null\n}"
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
                          "abc": {
                            "type": "array",
                            "items": {
                              "type": "object",
                              "properties": {
                                "datetime": {
                                  "type": "string",
                                  "example": "2016-04-01 00:00:00"
                                },
                                "value": {
                                  "type": "integer",
                                  "example": 20,
                                  "default": 0
                                }
                              }
                            }
                          },
                          "xyz": {
                            "type": "array",
                            "items": {
                              "type": "object",
                              "properties": {
                                "datetime": {
                                  "type": "string",
                                  "example": "2016-04-04 00:00:00"
                                },
                                "value": {
                                  "type": "integer",
                                  "example": 1000,
                                  "default": 0
                                }
                              }
                            }
                          }
                        }
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
        "deprecated": false,
        "x-readme": {
          "code-samples": [
            {
              "language": "curl",
              "code": "curl --request POST \\\n  --url https://api.flumetech.com/users/user_id/devices/device_id/query \\\n  --header 'content-type: application/json' \\\n  --header 'authorization: Bearer token' \\\n  --data '{\"queries\":[{\"request_id\":\"abc\",\"bucket\":\"MON\",\"since_datetime\":\"2016-04-04 01:00:00\",\"group_multiplier\":3},{\"request_id\":\"xyz\",\"bucket\":\"DAY\",\"since_datetime\":\"2016-04-04 01:00:00\",\"until_datetime\":\"2016-04-07 01:00:00\"}]}'"
            },
            {
              "language": "javascript",
              "code": "var request = require(\"request\");\n\nvar options = {\n  method: 'POST',\n  url: 'https://api.flumetech.com/users/user_id/devices/device_id/query',\n  headers: {'content-type': 'application/json', 'authorization': 'Bearer token'},\n  body: '{\"queries\":[{\"request_id\":\"abc\",\"bucket\":\"MON\",\"since_datetime\":\"2016-04-04 01:00:00\",\"group_multiplier\":3},{\"request_id\":\"xyz\",\"bucket\":\"DAY\",\"since_datetime\":\"2016-04-04 01:00:00\",\"until_datetime\":\"2016-04-07 01:00:00\"}]}'\n};\n\nrequest(options, function (error, response, body) {\n  if (error) throw new Error(error);\n\n  console.log(body);\n});\n",
              "name": "Node"
            },
            {
              "language": "ruby",
              "code": "require 'uri'\nrequire 'net/http'\nrequire 'openssl'\n\nurl = URI(\"https://api.flumetech.com/users/user_id/devices/device_id/query\")\n\nhttp = Net::HTTP.new(url.host, url.port)\nhttp.use_ssl = true\nhttp.verify_mode = OpenSSL::SSL::VERIFY_NONE\n\nrequest = Net::HTTP::Post.new(url)\nrequest[\"content-type\"] = 'application/json'\nrequest[\"authorization\"] = 'Bearer token'\nrequest.body = \"{ \\\"queries\\\": [{ \\\"request_id\\\": \\\"abc\\\", \\\"bucket\\\": \\\"MON\\\", \\\"since_datetime\\\": \\\"2016-04-04 01:00:00\\\", \\\"group_multiplier\\\": 3 }, { \\\"request_id\\\": \\\"xyz\\\", \\\"bucket\\\": \\\"DAY\\\", \\\"since_datetime\\\": \\\"2016-04-04 01:00:00\\\", \\\"until_datetime\\\": \\\"2016-04-07 01:00:00\\\" }] }\"\n\nresponse = http.request(request)\nputs response.read_body"
            },
            {
              "language": "javascript",
              "code": "var data = '{\"queries\":[{\"request_id\":\"abc\",\"bucket\":\"MON\",\"since_datetime\":\"2016-04-04 01:00:00\",\"group_multiplier\":3},{\"request_id\":\"xyz\",\"bucket\":\"DAY\",\"since_datetime\":\"2016-04-04 01:00:00\",\"until_datetime\":\"2016-04-07 01:00:00\"}]}';\n\nvar xhr = new XMLHttpRequest();\n\nxhr.addEventListener(\"readystatechange\", function () {\n  if (this.readyState === this.DONE) {\n    console.log(this.responseText);\n  }\n});\n\nxhr.open(\"POST\", \"https://api.flumetech.com/users/user_id/devices/device_id/query\");\nxhr.setRequestHeader(\"content-type\", \"application/json\");\nxhr.setRequestHeader(\"authorization\", \"Bearer token\");\n\nxhr.send(data);"
            },
            {
              "language": "python",
              "code": "import requests\n\nurl = \"https://api.flumetech.com/users/user_id/devices/device_id/query\"\n\nheaders = {\n    'Content-Type': 'application/json',\n    'Authorization': 'Bearer token'\n}\n\npayload = { \"queries\": [{ \"request_id\": \"abc\", \"bucket\": \"MON\", \"since_datetime\": \"2016-04-04 01:00:00\", \"group_multiplier\": 3 }, { \"request_id\": \"xyz\", \"bucket\": \"DAY\", \"since_datetime\": \"2016-04-04 01:00:00\", \"until_datetime\": \"2016-04-07 01:00:00\" }] }\n\nresponse = requests.request(\"POST\", url, json=payload, headers=headers)\n\nprint(response.text)"
            }
          ],
          "samples-languages": [
            "curl",
            "javascript",
            "ruby",
            "python"
          ]
        }
      }
    }
  },
  "x-readme": {
    "headers": [],
    "explorer-enabled": true,
    "proxy-enabled": true
  },
  "x-readme-fauxas": true,
  "_id": "58b70615b72a430f007f9f99:5822189209de110f0054e359"
}
```
