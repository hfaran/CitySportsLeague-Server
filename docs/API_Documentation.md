**This documentation is automatically generated.**

**Output schemas only represent `data` and not the full output; see output examples and the JSend specification.**

# /api/auth/playerlogin/?

    Content-Type: application/json

## POST


**Input Schema**
```json
{
    "properties": {
        "password": {
            "type": "string"
        },
        "username": {
            "type": "string"
        }
    },
    "required": [
        "username",
        "password"
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

POST the required credentials to get back a cookie

* `username`: Username
* `password`: Password



## GET


**Input Schema**
```json
null
```



**Output Schema**
```json
{
    "type": "string"
}
```



**Notes**

GET to check if authenticated.

Should be obvious from status code (403 vs. 200).



<br>
<br>

# /api/player/me/?

    Content-Type: application/json

## GET


**Input Schema**
```json
null
```



**Output Schema**
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
        "username": {
            "type": "string"
        }
    },
    "type": "object"
}
```



**Notes**

(Player only) GET to retrieve player info



<br>
<br>

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
            "enum": [
                "M",
                "F"
            ]
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



<br>
<br>

# /api/player/search/?

    Content-Type: application/json

## POST


**Input Schema**
```json
{
    "properties": {
        "query": {
            "type": "string"
        }
    },
    "type": "object"
}
```



**Output Schema**
```json
{
    "type": "array"
}
```



**Notes**

Search for players whose name starts with query



<br>
<br>

# /api/team/team/\(?P\<name\>\[a\-zA\-Z0\-9\_\]\+\)/?$

    Content-Type: application/json

## PUT


**Input Schema**
```json
{
    "properties": {
        "name": {
            "type": "string"
        },
        "sport": {
            "enum": [
                "Basketball",
                "Soccer"
            ]
        },
        "usernames": {
            "type": "array"
        }
    },
    "required": [
        "usernames",
        "name",
        "sport"
    ],
    "type": "object"
}
```



**Output Schema**
```json
{
    "properties": {
        "name": {
            "type": "string"
        }
    },
    "type": "object"
}
```



**Notes**

PUT to create a team

* `name`
* `usernames`: list of teammates to add (except yourself)
* `sport`: One of "Basketball" or "Soccer"



## GET


**Input Schema**
```json
null
```



**Output Schema**
```json
{
    "properties": {
        "name": {
            "type": "string"
        },
        "sport": {
            "enum": [
                "Basketball",
                "Soccer"
            ]
        },
        "usernames": {
            "type": "array"
        }
    },
    "type": "object"
}
```



**Notes**

Get team with `name`



<br>
<br>

# /api/team/team/?

    Content-Type: application/json

## PUT


**Input Schema**
```json
{
    "properties": {
        "name": {
            "type": "string"
        },
        "sport": {
            "enum": [
                "Basketball",
                "Soccer"
            ]
        },
        "usernames": {
            "type": "array"
        }
    },
    "required": [
        "usernames",
        "name",
        "sport"
    ],
    "type": "object"
}
```



**Output Schema**
```json
{
    "properties": {
        "name": {
            "type": "string"
        }
    },
    "type": "object"
}
```



**Notes**

PUT to create a team

* `name`
* `usernames`: list of teammates to add (except yourself)
* `sport`: One of "Basketball" or "Soccer"



## GET


**Input Schema**
```json
null
```



**Output Schema**
```json
{
    "properties": {
        "name": {
            "type": "string"
        },
        "sport": {
            "enum": [
                "Basketball",
                "Soccer"
            ]
        },
        "usernames": {
            "type": "array"
        }
    },
    "type": "object"
}
```



**Notes**

Get team with `name`


