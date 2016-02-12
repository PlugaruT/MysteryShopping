
## Research Methodology

**`POST`**:

- `scripts` : *id* (`ManyToManyField`)
- `questionnaires` : *id* (`ManyToManyField`)
- `number_of_evaluations` : *integer*
- `description` : *string* (`blank=True`)
- `project_id` : *id* (if provided will set this `ReseearchMethodology` to the provided `Project`)
- `places_to_assess_repr` : *representation* of `PlaceToAssess` (`many = True`)
- `people_to_assess_repr` : *representation* of `PersonToAssess` (`many = True`)

> example:
```json
{
    "places_to_assess_repr": [],
    "people_to_assess_repr": [],
    "project_id": null,
    "number_of_evaluations": null,
    "description": "",
    "scripts": [],
    "questionnaires": []
}
```

**`GET`**:

- `scripts` : *id* (`ManyToManyField`)
- `questionnaires` : *id* (`ManyToManyField`)
- `number_of_evaluations` : *integer*
- `description` : *string* (`blank=True`)
- `scripts_repr` : *representation* of `QuestionnaireScript` (`many = True, read_only = True`)
- `questionnaires_repr` : *representation* of `QuestionnaireTemplate` (`many = True, read_only = True`)
- `places_to_assess_repr` : *representation* of `PlaceToAssess` (`many = True`)
- `people_to_assess_repr` : *representation* of `PersonToAssess` (`many = True`)

> [example](projects\ example/researchmethodology.json)

## Project

**`POST`**:

- `company` : *id*
- `tenant` : *id*
- `project_manager_type` : *id* (for `ContentType`: `tenantproductmanager` or `tenantprojectmanager`)
- `project_manager_id` : *integer*
- `shoppers` : *id* (`ManyToManyField`)
- `consultants_repr` : *representation* of `TenantConsultants` (`many = True`)
- `research_methodology` : *representation* of `ResearchMethodology`  (`required = False`)
- `period_start` : `DateField`
- `period_end` : `DateField`

> example:
```json
{
    "project_workers_repr": [],
    "research_methodology": {
        "project_id": null,
        "number_of_evaluations": null,
        "description": "",
        "scripts": [],
        "questionnaires": []
    },
    "project_manager_id": null,
    "period_start": null,
    "period_end": null,
    "tenant": null,
    "company": null,
    "project_manager_type": null,
    "shoppers": []
}
```

**`GET`**:

- `company` : *id*
- `tenant` : *id*
- `project_manager_type` : *id* (for `ContentType`: `tenantproductmanager` or `tenantprojectmanager`)
- `project_manager_id` : *integer*
- `shoppers` : *id* (`ManyToManyField`)
- `research_methodology` : *id* (`null = True`)
- `period_start` : `DateField`
- `period_end` : `DateField`
- `company_repr` :  *representation* of `Company` (`read_only = True`)
- `shoppers_repr` = *representation* of `Shopper` (`many = True, read_only = True`)
- `project_manager_repr` = *representation* of `TenantProductManager` or `TenantProjectManager` (`read_only = True`)
- `project_workers_repr` = *representation* of `ProjectWorker` = `tenantproductmanager`, `tenantprojectmanager` `tenantconsultant` (`many = True`)

> [example](projects\ example/project	.json)

## Planned Evaluation

**`POST`**:

- `project` : *id*
- `shopper` : *id*
- `questionnaire_script` : *id*
- `questionnaire_template` : *id*
- `entity` : *id*
- `section` : *id* (`null = True`)
- `employee_type` : *id* (for `ContentType`: `clientmanager` or `clientemployee`)
- `project_manager_id` : *integer*
- `visit_type` : *string* (`choises = 'call', 'visit'`)

> example:
```json
{
    "employee_id": null,
    "visit_type": null,
    "project": null,
    "shopper": null,
    "questionnaire_script": null,
    "questionnaire_template": null,
    "entity": null,
    "section": null,
    "employee_type": null
}
```

**`GET`**:

- `project` : *id*
- `shopper` : *id*
- `questionnaire_script` : *id*
- `questionnaire_template` : *id*
- `entity` : *id*
- `section` : *id* (`null = True`)
- `employee_type` : *id* (for `ContentType`: `clientmanager` or `clientemployee`)
- `project_manager_id` : *integer*
- `visit_type` : *string* (`choises = 'call', 'visit'`)
- `project_repr` : *representation* of `Project` (`read_only = True`)
- `shopper_repr` : *representation* of `Shopper` (`read_only = True`)
- `questionnaire_script_repr` : *representation* of `QuestionnaireScript` (`read_only = True`)
- `entity_repr` : *representation* of `Entity` (`read_only = True`)
- `section_repr` : *representation* of `Section` (`read_only = True`)
- `employee_repr` : *representation* of `employee` = `clientmanager` or `clientemployee` (`read_only = True`)

> [example](projects\ example/plannedevaluation.json)

## Accomplished Evaluation

**`POST`**:

- `project` : *id*
- `shopper` : *id*
- `questionnaire_script` : *id*
- `questionnaire_template` : *id*
- `entity` : *id*
- `section` : *id* (`null = True`)
- `employee_type` : *id* (for `ContentType`: `clientmanager` or `clientemployee`)
- `project_manager_id` : *integer*
- `visit_type` : *string* (`choises = 'call', 'visit'`)
- `questionnaire` : *id*
- `time_accomplished` : `DateTimeField`

> example:
```json
{
    "employee_id": null,
    "visit_type": null,
    "time_accomplished": null,
    "project": null,
    "shopper": null,
    "questionnaire_script": null,
    "questionnaire_template": null,
    "entity": null,
    "section": null,
    "employee_type": null,
    "questionnaire": null
}
```

**`GET`**:

- `project` : *id*
- `shopper` : *id*
- `questionnaire_script` : *id*
- `questionnaire_template` : *id*
- `entity` : *id*
- `section` : *id* (`null = True`)
- `employee_type` : *id* (for `ContentType`: `clientmanager` or `clientemployee`)
- `project_manager_id` : *integer*
- `visit_type` : *string* (`choises = 'call', 'visit'`)
- `questionnaire` : *id*
- `time_accomplished` : `DateTimeField`
- `project_repr` : *representation* of `Project` (`read_only = True`)
- `shopper_repr` : *representation* of `Shopper` (`read_only = True`)
- `questionnaire_script_repr` : *representation* of `QuestionnaireScript` (`read_only = True`)
- `entity_repr` : *representation* of `Entity` (`read_only = True`)
- `section_repr` : *representation* of `Section` (`read_only = True`)
- `employee_repr` : *representation* of `employee` = `clientmanager` or `clientemployee` (`read_only = True`)

> [example](projects\ example/accomplishedevaluation.json)

## Evaluation Assessment Level

**`POST`**:

- `project` : *id*
- `previous_level` : *id* (`null = True`)
- `project_manager` : *id* (`null = True`)
- `consultants` : [*ids*] (`M2M field`)
- `level` : *integer*

> example:
```json
{
    "level": null,
    "project": null,
    "previous_level": null,
    "project_manager": null,
    "consultants": []
}
```

**`GET`**:

- `project` : *id*
- `previous_level` : *id*
- `project_manager` : *id*
- `consultants` : [*ids*]
- `level` : *integer*
- `next_level` : *id* (`read_only = True`)
- `project_manager_repr` : *representation* of `Project Manager` (`read_only = True`)
- `consultants_repr` : *representation* of `Consultant` (`many = True, read_only = True`)
- `comments` : *representation* of `Evaluation Comment` (`many = True, read_only = True`)

> [example](projects\ example/evaluationassessmentlevel.json)


## Evaluation Assessment Comment

**`POST`**:

- `commenter_id` : *integer*
- `commenter_type` : *id* (for `ContentType`: `tenantprojectmanager` or `tenantconsultant`)
- `evaluation_assessment_level` : *id*
- `comment` : *string* (`TextField`)

> example:
```json
{
    "commenter_id": null,
    "comment": "",
    "commenter_type": null,
    "evaluation_assessment_level": null
}
```

**`GET`**:

- `commenter_id` : *integer*
- `commenter_type` : *id* (for `ContentType`: `tenantprojectmanager` or `tenantconsultant`)
- `evaluation_assessment_level` : *id*
- `comment` : *string* (`TextField`)
- `commenter_repr` : *representation* of `Project Manager` or `Consultant` (`read_only = True`)

> example:
```json
{
    "id": 1,
    "commenter_repr": {
        "id": 1,
        "user": {
            "id": 3,
            "username": "alex_tenant_consultant",
            "first_name": "",
            "last_name": ""
        },
        "tenant_repr": {
            "id": 2,
            "name": "Magenta"
        },
        "type": "tenantconsultant",
        "tenant": 2
    },
    "commenter_id": 1,
    "comment": "fjsdkl fjsdlfj sadklfjsdkl fajsdklfasd;fsjdkl;",
    "commenter_type": 15,
    "evaluation_assessment_level": 4
}
```