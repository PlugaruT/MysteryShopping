# Industry

**`POST`**:

- `name` : *string*

> example:
```json
{
    "name": ""
}
```

**`GET`**:

- `name` : *string*

> example:
```json
{
    "id": 13,
    "name": "Industrie textilă"
}
```

# Company

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

> [example] (companies\ example/company.json)

# Department

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

> [example] (companies\ example/department.json)


# Entity

**`POST`**:

- `department` : *id* (`required = False`, it's not required when you create in bulk: you send to the `department` endpoint the data about `entities`)
- `sector` : *id* (`null = True`)
- `city` : *id* 
- `tenant` : *id*
- `sections` : `SectionSerializer` (`many=True`)
- `name` : *string*
- `address` : *string*
- `coordinates` : *string* (`null = True`)

> example:
```json
{
    "sections": [],
    "name": "",
    "address": "",
    "coordinates": "",
    "department": null,
    "sector": null,
    "city": null,
    "tenant": null
}
```

**`GET`**:
- `department` : *id*
- `sector` : *id*
- `city` : *id*
- `tenant` : *id*
- `manager` : `GenericRelation` of `Entity` manager
- `sections` : `SectionSerializer` (`many=True`)
- `name` : *string*
- `address` : *string*
- `coordinates` : *string*

> [example](comanies\ example/entity.json)

# Section

**`POST`**:

- `entity` : *id* (`required = False`, it's not required when you create in bulk: you send to the `department` endpoint the data about the `sections` which are within `entities`)
- `tenant` : *id*
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

> [example](comanies\ example/section.json)