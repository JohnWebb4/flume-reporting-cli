Accessing the API

Fetch the complete documentation index at: https://flumetech.readme.io/llms.txt. Use this file to discover all available pages before exploring further. Append .md to any documentation page URL to get its markdown version.

# Accessing the API

Follow these instructions to get personal access to the API.

[block:api-header]
{
  "type": "basic",
  "title": "1. Log in to the Flume Customer Portal"
}
[/block]

First, click this link to go to the portal: <a href="https://portal.flumetech.com" target="_blank">Customer Portal</a>

Log in using your username and password.

[block:api-header]
{
  "title": "2. Generate your access tokens"
}
[/block]

Go to the Settings page, and scroll down to the bottom. Click on the "Generate API Client" button.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/a90c020-api_access.png",
        "api_access.png",
        2880,
        1634,
        "#edf1f1"
      ]
    }
  ]
}
[/block]

Your credentials should now be displayed. You can always access them again in the Settings page on the portal.

[block:api-header]
{
  "title": "3. Authenticating with the API"
}
[/block]

Use your access token by passing it in a Bearer Authorization header like this:

```
Authorization: Bearer YOUR_KEY_HERE
```

Most routes require the JWT access token to be present to return a result.

Using the client provided by the online Portal will only permit the user who requested the client to access the API.

If you access token expires, it must be refreshed with the refresh token.
This can be done through the [Refresh Access Token](https://flumetech.readme.io/reference/refresh-access-token-1) route.

Important: Once you have a new access token, delete your old access token. This is for security purposes, because the old token is not automatically invalidated, and will continue to work until it expires.
