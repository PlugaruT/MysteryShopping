## Client Manager

**`POST`**:

- `company` : *id* 
- `user` : `User` representation
- `place_id` : *integer*
- `place_type` : *id* (for `ContentType` : `department`, `entity`, `section`)

> example:
```json
{
    "place_id": null,
    "user": { ... },
    "company": null,
    "place_type": null
}
```

**`GET`**:

- `company` : *id* 
- `user` : *id*
- `place_id` : *integer*
- `place_type` : *id* (for `ContentType` : `department`, `entity`, `section`)
- `manager_repr` : *representation* of `User` (`read_only = True`)

> example: 
```json
{
    "id": 1,
    "manager_repr": {
        "username": "ion_client_manager",
        "first_name": "",
        "last_name": ""
    },
    "place_id": 1,
    "user": 2,
    "company": 1,
    "place_type": 24
}
```

## Client Employee

**`POST`**:

- `company` : *id* 
- `user` : *id*
- `entity` : *id*
- `section` : *id* (`null = True`)

> example:
```json
{
    "user": null,
    "company": null,
    "entity": null,
    "section": null
}
```

**`GET`**:

- `company` : *id* 
- `user` : *id*
- `entity` : *id*
- `section` : *id* (`null = True`)
- `employee_repr` : *representation* of `User` (`read_only = True`)

> example: 
```json
{
    "id": 1,
    "employee_repr": {
        "username": "andrei_client_employee",
        "first_name": "",
        "last_name": ""
    },
    "user": 6,
    "company": 1,
    "entity": 1,
    "section": 1
}
```
