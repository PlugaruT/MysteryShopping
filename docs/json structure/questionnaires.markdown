## Questionnaire Script

**`POST`**:

- `title` : *string* (`max_length = 100`)
- `description` : *string*

> example:
```json
{
    "title": "",
    "description": ""
}
```

**`GET`**:
- `title` : *string* (`max_length = 100`)
- `description` : *string*

> example:
```json
{
    "id": 1,
    "title": "Script#1",
    "description": "Bacon ipsum dolor amet rump bresaola kielbasa, cow turducken venison pig ..."
}
```

## Template Questionnaire

**`POST`**:

- `title` : *string* (`max_length = 100`)
- `tenant` : *id*
- `description` : *string*
- `template_blocks` : *representation* for `QuestionnaireTemplateBlock` (`many = True, required = False`)

> example:
```json
{
    "template_blocks": [],
    "title": "",
    "description": "",
    "tenant": null
}
```

**`GET`**:

- `title` : *string* (`max_length = 100`)
- `tenant` : *id*
- `description` : *string*
- `template_blocks` : *representation* for `QuestionnaireTemplateBlock` (`many = True, required = False`)

> [example](questionnaires\ example/templatequestionnaire.json)

## Questionnaire Template Block

**`POST`**:

- `title` : *string* (`max_length = 50`)
- `weight` : *DecimalField* (`max_digits=5, decimal_places=4`, example: `0.4552`)
- `questionnaire_template` : *id*
- `parent_block` : *id* to `self` (`null = True`)
- `lft` : *integer* (`required = False`)
- `rght` : *integer* (`required = False`)
- `level` : *integer* (`required = False`)
- `tree_id` : *integer* (`required = False`)
- `template_block_questions` : *representation* of `QuestionnaireTemplateBlock` (`many = True`)

The `lft`, `rght`, `level` and `tree_id` fields are used by the **mptt** algorithm. If provided, the data will override the data calculated by the algorithm, if not, the values will be set by the algorithm.

> example:
```json
{
    "template_block_questions": [],
    "questionnaire_template": null,
    "lft": null,
    "rght": null,
    "tree_id": null,
    "level": null,
    "title": "",
    "weight": null,
    "parent_block": null
}
```

**`GET`**:

- `title` : *string*
- `weight` : *DecimalField*
- `questionnaire_template` : *id*
- `parent_block` : *id* to `self`
- `lft` : *integer*
- `rght` : *integer*
- `level` : *integer*
- `tree_id` : *integer*
- `template_block_questions` : *representation* of `QuestionnaireTemplateBlock` (`many = True`)

> [example](projects\ example/questionnairetemplateblock.json)

## Questionnaire Template Question

**`POST`**:

- `question_body` : *string* (`max_length = 200`)
- `type` : *string*
- `max_score` : *integer* (`null = True`)
- `questionnaire_template` : *id*
- `template_block` : *id*

> example:
```json
{
    "questionnaire_template": null,
    "template_block": null,
    "question_body": "",
    "type": "",
    "max_score": null
}
```

**`GET`**:

- `question_body` : *string*
- `type` : *string*
- `max_score` : *integer*
- `questionnaire_template` : *id*
- `template_block` : *id*

> example:
```json
{
    "id": 1,
    "questionnaire_template": 2,
    "template_block": 3,
    "question_body": "Question#1",
    "type": "sYes [::] 5 || No [::] 0 || NA [::] -1",
    "max_score": 2
}
```