## Company

**`POST`**:

- `industry` : *id* 
- `country` : *id* 
- `tenant` : *id*
- `name` : *string*
- `contact_person` : *string*
- `contact_phone` : *string*
- `contact_email` : *string*
- `domain` : *string*
- `logo` : *image* (`null = True`)

> example:
```json
{
    "name": "",
    "contact_person": "",
    "contact_phone": "",
    "contact_email": "",
    "domain": "",
    "logo": null,
    "industry": null,
    "country": null,
    "tenant": null
}
```

**`GET`**:

- `industry` : *id* 
- `country` : *id* 
- `tenant` : *id*
- `name` : *string*
- `contact_person` : *string*
- `contact_phone` : *string*
- `contact_email` : *string*
- `domain` : *string*
- `logo` : *image* (`null = True`)
- `departments_repr` : *representation* of `Departments` (`many=True`)

> example:
```json
{
    "id": 1,
    "departments_repr": [
        {
            "id": 2,
            "manager": [],
            "entities": [],
            "name": "fsd",
            "company": 1,
            "tenant": 1
        },
        {
            "id": 1,
            "manager": [
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
            ],
            "entities": [
                {
                    "id": 1,
                    "manager": [
                        {
                            "id": 2,
                            "manager_repr": {
                                "username": "mark_entity_manager",
                                "first_name": "",
                                "last_name": ""
                            },
                            "place_id": 1,
                            "user": 7,
                            "company": 1,
                            "place_type": 25
                        }
                    ],
                    "sections": [
                        {
                            "id": 1,
                            "manager": [
                                {
                                    "id": 3,
                                    "manager_repr": {
                                        "username": "vera_section_manager",
                                        "first_name": "",
                                        "last_name": ""
                                    },
                                    "place_id": 1,
                                    "user": 8,
                                    "company": 1,
                                    "place_type": 26
                                }
                            ],
                            "entity": 1,
                            "tenant": 2,
                            "name": "Mars"
                        }
                    ],
                    "tenant": 2,
                    "department": 1,
                    "name": "Space Exploration",
                    "address": "lalala, classified",
                    "coordinates": "123 123",
                    "sector": 1,
                    "city": 1
                }
            ],
            "name": "Space Rockets",
            "company": 1,
            "tenant": 1
        }
    ],
    "name": "NASA",
    "contact_person": "Leroy Jenkins",
    "contact_phone": "+123",
    "contact_email": "help@nasa.com",
    "domain": "nasa",
    "logo": null,
    "industry": 1,
    "country": 1,
    "tenant": 1
}
```

## Department

**`POST`**:

- `company` : *id* 
- `tenant` : *id* 
- `name` : *string*
- `entities` : `EntitySerializer` (`many=True`)

```json
{
    "entities": [],
    "name": "",
    "company": null,
    "tenant": null
}
```

**`GET`**:

- `company` : *id* 
- `tenant` : *id* 
- `name` : *string*
- `manager` : `GenericRelation` of `Department` manager
- `entities` : `EntitySerializer` (`many=True`)

> example: 
```json
{
    "id": 1,
    "manager": [
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
    ],
    "entities": [
        {
            "id": 1,
            "manager": [
                {
                    "id": 2,
                    "manager_repr": {
                        "username": "mark_entity_manager",
                        "first_name": "",
                        "last_name": ""
                    },
                    "place_id": 1,
                    "user": 7,
                    "company": 1,
                    "place_type": 25
                }
            ],
            "sections": [
                {
                    "id": 1,
                    "manager": [
                        {
                            "id": 3,
                            "manager_repr": {
                                "username": "vera_section_manager",
                                "first_name": "",
                                "last_name": ""
                            },
                            "place_id": 1,
                            "user": 8,
                            "company": 1,
                            "place_type": 26
                        }
                    ],
                    "entity": 1,
                    "tenant": 2,
                    "name": "Mars"
                }
            ],
            "tenant": 2,
            "department": 1,
            "name": "Space Exploration",
            "address": "lalala, classified",
            "coordinates": "123 123",
            "sector": 1,
            "city": 1
        }
    ],
    "name": "Space Rockets",
    "company": 1,
    "tenant": 1
}
```

## Entity

**`POST`**:

- `department` : *id* (`required = False`)
- `sector` : *id* (`null = True`)
- `city` : *id* 
- `tenant` : *id* (`required = False`)
- `sections` : `SectionSerializer` (`many=True`)
- `name` : *string*
- `address` : *string*
- `coordinates` : *string* (`null = True`)

> example:
```json
{
    "sections": [],
    "tenant": null,
    "department": null,
    "name": "",
    "address": "",
    "coordinates": "",
    "sector": null,
    "city": null
}
```

**`GET`**:
- `department` : *id* 
- `sector` : *id* (`null = True`)
- `city` : *id*
- `tenant` : *id*
- `manager` : `GenericRelation` of `Entity` manager
- `sections` : `SectionSerializer` (`many=True`)
- `name` : *string*
- `address` : *string*
- `coordinates` : *string* (`null = True`)

> example:
```json
{
    "id": 1,
    "manager": [
        {
            "id": 2,
            "manager_repr": {
                "username": "mark_entity_manager",
                "first_name": "",
                "last_name": ""
            },
            "place_id": 1,
            "user": 7,
            "company": 1,
            "place_type": 25
        }
    ],
    "sections": [
        {
            "id": 1,
            "manager": [
                {
                    "id": 3,
                    "manager_repr": {
                        "username": "vera_section_manager",
                        "first_name": "",
                        "last_name": ""
                    },
                    "place_id": 1,
                    "user": 8,
                    "company": 1,
                    "place_type": 26
                }
            ],
            "entity": 1,
            "tenant": 2,
            "name": "Mars"
        }
    ],
    "tenant": 2,
    "department": 1,
    "name": "Space Exploration",
    "address": "lalala, classified",
    "coordinates": "123 123",
    "sector": 1,
    "city": 1
}
```

## Section

**`POST`**:

- `entity` : *id* (`required = False`)
- `tenant` : *id* (`required = False`)
- `name` : *string*

> example:
```json
{
    "entity": null,
    "tenant": null,
    "name": ""
}
```

**`GET`**:

- `entity` : *id* (`required = False`)
- `tenant` : *id* (`required = False`)
- `name` : *string*
- `manager` : `GenericRelation` of `Section` manager

> example: 
```json
{
    "id": 1,
    "manager": [
        {
            "id": 3,
            "manager_repr": {
                "username": "vera_section_manager",
                "first_name": "",
                "last_name": ""
            },
            "place_id": 1,
            "user": 8,
            "company": 1,
            "place_type": 26
        }
    ],
    "entity": 1,
    "tenant": 2,
    "name": "Mars"
}
```