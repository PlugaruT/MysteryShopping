## Overview Dashboard
### *endpoint*: `^api/v1/cxi/overview/`

#### Query Parameters
`project` : indicates the `id` of the *project* <br>
`entity` : (*not required*) indicates the `id` of the *entity*

**`GET`**:
It returns a dictionary with the *type indicators* of the `cxi` question as the `key` and a *dictionary* for the `value`.
The each dictionary contains the same `4` values:
- `promoters`
- `passibes`
- `detractors`
- `indicator` (*final score*) <br>
and the `project_comment`, if it exists, if not the value returned will be `null`

> example
```json
{
    "NPS": {
        "detractors": 56.25,
        "promoters": 37.5,
        "passives": 6.25,
        "indicator": -18.75
    },
    "project_comment": {
        "id": 5,
        "indicator": "",
        "general": "Overview comment important",
        "dynamics": "",
        "details": "",
        "causes": "",
        "project": 10,
        "entity": null
    }
}
```


## Indicator Dashboard
### *endpoint*: `^api/v1/cxi/indicator/`

#### Query Parameters
`project` : indicates the `id` of the *project* <br>
`indicator` : indicates the `type` of the *indicator question* you want to get the indicator data for<br>
`entity` : (*not required*) indicates the `id` of the *entity*

**`GET`**:
It returns a dictionary with `4` entries:
- `general` : returns the same `4` fields like in `Overview Dashboard`
- `coded_causes` : returns a `list` of *coded causes* and the number of times they are used.
	- `count` : number of times is't used
	- `coded_cause`: serialized instance of the `coded_cause`
- `details` : returns a `list` of `dicts`. Each dictionary contains:
	- `item_label` : the body of the *indicator question* (and once for each `response` it will be `"Entities"` which will signify that this data if for each individual `entity` from the `project)
	- `results` : a `list` with choices that the *indicator question* contains (and sometimes with the `"other"` value when the `choice` selected was not from the available ones):
		- `score`: returns the same `4` fields like in `Overview Dashboard` and `general`
		- `choice` : the *choice* `text` (for the `"Entities"` field this will contain the `name` of the `Entity`)
		- `number_of_respondents` : number of people that selected this `choice` (or responded for the particular `Entity`)
		- `other_answer_choices` : usually left *empty*, used when the `"other"` choice was selected and contains a list of all those choices.
- `project_comment` : *representation* of a `ProjectComment`

> [example](cxi\ example/indicator_dashboard.json)


## Indicator Dashboard List
### *endpoint*: `^api/v1/cxi/indicatorlist/`

#### Query Parameters
`project` : indicates the `id` of the *project* from which you want to get the `indicators` <br>
`company` : indicates the `id` of the *company* from which *projects*  you want to get the `indicators`

If both the `project` and the `company` have been sent as query params, the algorithm will use the `company`'s id, as it incapsulates the `project`'s one.

**`GET`**:
It returns a list with `variable` length which will contain `indicator` names

> example:
```json
[
    "NPS",
    "Enjoyability"
]
```

## Coded Cause Label

**`POST`**:

- `name` : *char* (`max_length = 50`)
- `tenant` : *id* to `Tenant`

> example:
```json
{
    "name": "",
    "tenant": null
}
```

**`GET`**:
- `id` : *int*
- `name` : *char* (`max_length = 50`)
- `tenant` : *id* to `Tenant`

> example:
```json
{
    "id": 1,
    "name": "Coded 1",
    "tenant": 1
}
```


## Coded Cause

**`POST`**:

- `coded_label` : *representation* for `CodedCauseLabel`
- `type` : *string* (`max_length=30, blank=True`)
- `sentiment` : *string* (`max_length=1`, choices: `a` (for 'apreciation') or `f` (for 'frustration'))
- `tenant` : *id* to `Tenant`
- `parent` : `id` to `self` (`null=True`)

> example:
```json
{
    "coded_label": {
        "name": "",
        "tenant": null
    },
    "type": "",
    "sentiment": null,
    "tenant": null,
    "parent": null
}
```

**`GET`**:

- `id` : *int*
- `coded_label` : *representation* for `CodedCauseLabel`
- `type` : *string* (`max_length=30, blank=True`)
- `sentiment` : *string* (`max_length=1`)
- `tenant` : *id* to `Tenant`
- `parent` : `id` to `self` (`null=True`)


> example:
```json
{
    "id": 8,
    "coded_label": {
        "id": 1,
        "name": "Coded 1",
        "tenant": 1
    },
    "type": "NPS",
    "sentiment": "a",
    "tenant": 1,
    "parent": null
}
```

## Project Comment

**`POST`**:

- `indicator` : *string* (`max_length=30, blank=True`, left blank if it's for the `overview`)
- `general` : *string* (`blank=True`)
- `dynamics` : *string* (`blank=True`)
- `details` : *string* (`blank=True`)
- `causes` : *string* (`blank=True`)
- `project` : *id* for `Project`
- `entity` : *id* for `Entity` (`null=True`)

> example:
```json
{
    "indicator": "",
    "general": "",
    "dynamics": "",
    "details": "",
    "causes": "",
    "project": null,
    "entity": null
}
```

**`GET`**:

- `id` : *int*
- `indicator` : *string* (`max_length=30, blank=True`, left blank if it's for the `overview`)
- `general` : *string* (`blank=True`)
- `dynamics` : *string* (`blank=True`)
- `details` : *string* (`blank=True`)
- `causes` : *string* (`blank=True`)
- `project` : *id* for `Project`
- `entity` : *id* for `Entity` (`null=True`)

> example:
```json
{
    "id": 4,
    "indicator": "NPS",
    "general": "NPS comment important, no entity",
    "dynamics": "",
    "details": "",
    "causes": "",
    "project": 10,
    "entity": null
}
```

