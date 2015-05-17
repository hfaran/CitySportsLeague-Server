**This documentation is automatically generated.**

**Output schemas only represent `data` and not the full output; see output examples and the JSend specification.**

# /api/player/player/?

    Content-Type: application/json

## PUT


**Input Schema**
```json
{
    "properties": {
        "bio": {
            "type": "string"
        },
        "birthday": {
            "type": "string"
        },
        "city": {
            "type": "string"
        },
        "country": {
            "type": "string"
        },
        "first": {
            "type": "string"
        },
        "gender": {
            "type": "string"
        },
        "last": {
            "type": "string"
        },
        "password": {
            "type": "string"
        },
        "username": {
            "type": "string"
        }
    },
    "required": [
        "username",
        "first",
        "last",
        "password",
        "birthday",
        "city",
        "country"
    ],
    "type": "object"
}
```



**Output Schema**
```json
{
    "properties": {
        "username": {
            "type": "string"
        }
    },
    "type": "object"
}
```



**Notes**

PUT the required parameters to permanently register a new player

* `username`
* `first`: First name
* `last`: Last name
* `password`: Password for future logins
* `gender`: M/F
* `birthday`: e.g., "1993-05-16"
* `city`
* `country`
* `bio`


