## Questionnaire Script

**`POST`**:

- `title` : *char* (`max_length = 100`)
- `description` : *string*

> example:
```json
{
    "title": "",
    "description": ""
}
```

**`GET`**:
- `id` : *int*
- `title` : *char* (`max_length = 100`)
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
- `type`: *char* (`max_length = 1`, can be either `m` for Mystery Shopping Questionnaire, and `c` for Customer Experience Index Questionnaire)
- `description` : *string*
- `template_blocks` : *representation* for `QuestionnaireTemplateBlock` (`many = True, required = False`)

> example:
```json
{
    "template_blocks": [],
    "title": "",
    "type": null,
    "description": "",
    "tenant": null
}
```

**`GET`**:

- `title` : *string* (`max_length = 100`)
- `tenant` : *id*
- `type`: *char* (`max_length = 1`, can be either `m` for Mystery Shopping Questionnaire, and `c` for Customer Experience Index Questionnaire)
- `description` : *string*
- `template_blocks` : *representation* for `QuestionnaireTemplateBlock`

> [example](questionnaires\ example/templatequestionnaire.json)

## Questionnaire Template Block

**`POST`**:

- `title` : *string* (`max_length = 50`)
- `weight` : *DecimalField* (`max_digits=5, decimal_places=2`, example: `45.52`)
- `questionnaire_template` : *id*
- `parent_order_number` : *integer* to that shows the theoretical `parent_block` (`required = False, null = True`, only used when within `Questionnaire Template` JSON)
- `order_number` : *integer* (`required = False`, identifier of the block inside the *sent* template `questionnaire`, only used when within `Questionnaire Template` JSON)
- `template_questions` : *representation* of `QuestionnaireTemplateBlock` (`many = True`)
- `parent_block` : *id* (`required = False`, for `QuestionnaireTemplateBlock`)
- `order` : *integer* (used to define the order of the block within the `Questionnaire Template`)
- `siblings` : *JSON* (`list`, only required when updating a `Questionnaire Template` with new blocks. It will contain information to update for the blocks on the same level and the same parent (if it has one) as the new block. Each element of the `list` will contain a structure with `block_id` that will indicate the `id` of the block to update and a structure with the `block_changes` key that will contain the fields to update)

> `siblings` structure:
```json
[
	{
        "block_id": 1,
        "block_changes": {
            "weight": 2
        }
    },
    {
    	"block_id": 2,
        "block_changes": {
            "weight": 5,
            "title": "New old block name"
        }
    }
]
```

> example:
```json
{
    "template_questions": [],
    "parent_order_number": null,
    "order_number": null,
    "siblings": null,
    "title": "",
    "weight": null,
    "order": null,
    "questionnaire_template": null,
    "parent_block": null
}
```

**`GET`**:

- `id` : *int*
- `title` : *string*
- `weight` : *DecimalField*
- `questionnaire_template` : *id*
- `parent_block` : *id* to `self`
- `lft` : *int*
- `rght` : *int*
- `level` : *int*
- `tree_id` : *int*
- `template_block_questions` : *representation* of `QuestionnaireTemplateBlock` (`many = True`)
- `order` : *integer* (used to define the order of the block within the `Questionnaire Template`)

> [example](questionnaires\ example/questionnairetemplateblock.json)

## Questionnaire Template Question

**`POST`**:

- `question_body` : *string* (`max_length = 200`)
- `type` : *string* (can be one of: ```text_field = 't', date_field = 'd', single_choice = 's', multiple_choice = 'm', nps_question = 'n', enjoyability_question = 'j', easiness_question = 'e', usefulness_question = 'u'```)
- `max_score` : *integer* (`null = True`)
- `questionnaire_template` : *id*
- `template_block` : *id*
- `order` : *integer* (used to define the order of the question within the `Questionnaire Template Block`)
- `siblings` : *JSON* (`list` same concept as for the `siblings` from `Questionnaire Template Block`, but the `questions` are from the same `block`)
- `show_comment` : *bool*
- `template_question_choices`: *representation* for `QuestionnaireTemplateQuestionChoice` (`many = True, required = False`, structure will be defined below)
- `weight` : *DecimalField* (`max_digits=5, decimal_places=2`, example: `45.52`)

> `siblings` structure:
```json
[
	{
        "question_id": 1,
        "question_changes": {
            "weight": 2
        }
    },
    {
    	"question_id": 2,
        "question_changes": {
            "max_score": 5,
            "question_body": "New old question body name",
            "weight": 11
        }
    }
]
```

> example:
```json
{
    "template_question_choices": [],
    "siblings": null,
    "question_body": "",
    "type": null,
    "max_score": null,
    "order": null,
    "weight": null,
    "show_comment": false,
    "questionnaire_template": null,
    "template_block": null
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
    "id": 48,
    "template_question_choices": [
        {
            "id": 87,
            "text": "Da",
            "score": "3.00",
            "weight": "0.50",
            "order": 1,
            "template_question": 48
        },
        {
            "id": 88,
            "text": "Nu",
            "score": "0.00",
            "weight": "0.50",
            "order": 2,
            "template_question": 48
        }
    ],
    "question_body": "E soare?",
    "type": "s",
    "max_score": 3,
    "order": 2,
    "weight": "50.00",
    "show_comment": true,
    "questionnaire_template": 8,
    "template_block": 23
}
```

## Template Question Choice

**`POST`**:

- `text` : *string* (`max_length = 255`)
- `score` : *integer*
- `weight` : *DecimalField* (`max_digits=5, decimal_places=4`, example: `0.4552`)
- `template_question` : *representation* for `QuestionnaireTemplateQuestion` (`many = True, required = False`)
- `order` : *integer* (used to define the order of the question choice within the `Questionnaire Template Question`)


> example:
```json
{
    "text": "",
    "score": null,
    "weight": null,
    "order": null,
    "template_question": null
}
```

**`GET`**:

- `id` : *int*
- `text` : *string* (`max_length = 255`)
- `score` : *integer*
- `weight` : *DecimalField* (`max_digits=5, decimal_places=4`, example: `0.4552`)
- `template_question` : *representation* for `QuestionnaireTemplateQuestion` (`many = True, required = False`)
- `order` : *integer* (used to define the order of the question choice within the `Questionnaire Template Question`)

> example:
```json
{
    "id": 47,
    "text": "Da",
    "score": "3.00",
    "weight": "0.50",
    "order": 1,
    "template_question": 24
}
```