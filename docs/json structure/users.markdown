## User

**`POST`**:

- `username` : *char* (30 characters or fewer. Letters, digits and @/./+/-/_ only.)
- `email`: *char*
- `first_name` : *char*
- `last_name` : *char*
- `change_username` : *bool* (`required = False`, `write_only = True`. Set to `True` if the user has changed it's `username`)
- `password` : *char* (`max_length = 128`)
- `confirm_password` : *char* (`max_length = 128`, `user` will be created only if this field matches with the `password` field)

> example:
```json
{
    "username": "",
    "email": "",
    "first_name": "",
    "last_name": "",
    "change_username": false,
    "password": "",
    "confirm_password": ""
}
```

**`GET`**:

- `id` : *int*
- `username` : *char* (30 characters or fewer. Letters, digits and @/./+/-/_ only.)
- `email`: *char*
- `first_name` : *char*
- `last_name` : *char*
- `roles` : *list* (will contain a list of roles that the user has: `tenantproductmanager`, `tenantprojectmanager`, `tenantconsultant`, `shopper`, `collector`, `clientprojectmanager`, `clientmanager`, `clientemployee` or `admin`. It will usually be one role, but it can be a combination of the above mentioned)\
- `shopper` : *id* (used to check whether the `user` is a `collector`, which is a type of `shopper`)

> example:
```json
{
    "id": 24,
    "username": "example_user",
    "email": "example@user.com",
    "first_name": "User",
    "last_name": "Example",
    "roles": [
    	"tenantproductmanager",
        "tenantprojectmanager",
        "admin"
    ],
    "shopper": null
}
```

## Client Manager

**`POST`**:

- `company` : *id*
- `first_name` : *char* (`max_length = 30`)
- `last_name` : *char* (`max_length = 30`)
- `job_title` : *char*
- `user` : `User` representation (documented above)
- `place_id` : *integer* (*id*)
- `place_type` : *id* (for `ContentType` : `department` - `24`, `entity` - `25`, `section` - `26`)
- `tenant` : *id*

> example:
```json
{
    "user": {...},
    "first_name": "",
    "last_name": "",
    "job_title": "",
    "place_id": null,
    "tenant": null,
    "company": null,
    "place_type": null
}
```

**`GET`**:

- `id` : *int*
- `company` : *id*
- `user` : `User` representation
- `first_name` : *char* (`max_length = 30`)
- `last_name` : *char* (`max_length = 30`)
- `job_title` : *char*
- `place_id` : *integer*
- `place_type` : *id* (for `ContentType` : `department` - `24`, `entity` - `25`, `section` - `26`)
- `tenant` : *id*

> example:
```json
{
    "id": 4,
    "user": {
        "id": 25,
        "username": "client_manager",
        "email": "client@manager.com",
        "first_name": "Client",
        "last_name": "Manager",
        "roles": [
            "clientmanager"
        ],
        "shopper": null
    },
    "first_name": "Client",
    "last_name": "Manger",
    "job_title": "very important manager",
    "place_id": 1,
    "tenant": 1,
    "company": 1,
    "place_type": 24
}
```

## Client Employee

**`POST`**:

- `company` : *id*
- `entity` : *id*
- `section` : *id* (`null = True`)
- `first_name` : *char* (`max_length = 30`)
- `last_name` : *char* (`max_length = 30`)
- `job_title` : *char*
- `user` : `User` representation (documented above)
- `tenant` : *id*

> example:
```json
{
    "user": {...},
    "first_name": "",
    "last_name": "",
    "job_title": "",
    "tenant": null,
    "company": null,
    "entity": null,
    "section": null
}
```

**`GET`**:

- `id` : *int*
- `company` : *id*
- `company_repr` : `Company` representation
- `entity` : *id*
- `section` : *id*
- `first_name` : *char* (`max_length = 30`)
- `last_name` : *char* (`max_length = 30`)
- `job_title` : *char*
- `user` : `User` representation (documented above)
- `tenant` : *id*

> example:
```json
{
    "id": 2,
    "user": {
        "id": 26,
        "username": "client_employee1",
        "email": "client@employee.com",
        "first_name": "Client",
        "last_name": "Employee",
        "roles": [],
        "shopper": null
    },
    "company_repr": {
        "id": 1,
        "name": "NASA",
        "contact_person": "Leroy Jenkins",
        "contact_phone": "1234",
        "contact_email": "help@nasa.com",
        "domain": "nasa.com",
        "logo": null,
        "industry": 1,
        "country": 1,
        "tenant": 1
    },
    "first_name": "Client",
    "last_name": "Employee",
    "job_title": "barman",
    "tenant": 1,
    "company": 1,
    "entity": 1,
    "section": null
}
```
