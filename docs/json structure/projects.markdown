
## Research Methodology

**`POST`**:

- `scripts` : *id* (`ManyToManyField`)
- `questionnaires` : *id* (`ManyToManyField`)
- `number_of_evaluations` : *integer*
- `description` : *string* (`blank=True`)
- `project_id` : *id* (if provided will set this `ReseearchMethodology` to the provided `Project`)
- `places_to_assess_repr` : *representation* of `PlaceToAssess` (`many = True`)
- `people_to_assess_repr` : *representation* of `PersonToAssess` (`many = True`)
- `tenant` : *id*

> example:
```json
{
    "scripts": [],
    "places_to_assess_repr": [],
    "people_to_assess_repr": [],
    "project_id": null,
    "number_of_evaluations": null,
    "description": "",
    "tenant": null,
    "questionnaires": []
}
```

**`GET`**:

- `id` : *int*
- `scripts` : *id* (`ManyToManyField`)
- `questionnaires` : *id* (`ManyToManyField`)
- `number_of_evaluations` : *integer*
- `description` : *string* (`blank=True`)
- `scripts_repr` : *representation* of `QuestionnaireScript` (`many = True, read_only = True`)
- `questionnaires_repr` : *representation* of `QuestionnaireTemplate` (`many = True, read_only = True`)
- `places_to_assess_repr` : *representation* of `PlaceToAssess` (`many = True`)
- `people_to_assess_repr` : *representation* of `PersonToAssess` (`many = True`)
- `tenant` : *id*

> [example](projects\ example/researchmethodology.json)

## Project

**`POST`**:

- `company` : *id*
- `tenant` : *id*
- `project_manager` : *id* (for `TenantProjectManager`)
- `shoppers` : *id* (`ManyToManyField`)
- `consultants_repr` : *representation* of `TenantConsultants` (`many = True`)
- `research_methodology` : *representation* of `ResearchMethodology`  (`required = False`)
- `period_start` : `DateField`
- `period_end` : `DateField`

> example:
```json
{
    "research_methodology": {...},
    "shoppers": [],
    "period_start": null,
    "period_end": null,
    "type": null,
    "tenant": null,
    "company": null,
    "project_manager": null,
    "consultants": []
}
```

**`GET`**:

- `id` : *id*
- `company` : *id*
- `tenant` : *id*
- `project_manager_type` : *id* (for `ContentType`: `tenantproductmanager` or `tenantprojectmanager`)
- `project_manager` : *id*
- `shoppers` : *id* (`ManyToManyField`)
- `research_methodology` : *id* (`null = True`)
- `period_start` : `DateField`
- `period_end` : `DateField`
- `company_repr` :  *representation* of `Company` (`read_only = True`)
- `shoppers_repr` = *representation* of `Shopper` (`many = True, read_only = True`)
- `project_manager_repr` = *representation* of `TenantProductManager` or `TenantProjectManager` (`read_only = True`)
- `project_workers_repr` = *representation* of `ProjectWorker` = `tenantproductmanager`, `tenantprojectmanager` `tenantconsultant` (`many = True`)
- `evaluation_assessment_levels_repr` : *representation* of `EvaluationAssessmentLevels`
- `type` : *char* (can be `m` or `c`, exactly like for `questionnaires`)
- `cxi_indicators` : *dict* that contains:
    - `indicator_list`: *list* that has all the indicators, it may be `empty`
    - `detail`: *str* it is present when an `error` has occured (contains error details)

> [example](projects\ example/project.json)

## Evaluation

**`POST`**:

- `project` : *id*
- `shopper` : *id*
- `questionnaire_script` : *id*
- `questionnaire_template` : *id* (it will take this `questionnaire template` and create a `questionnaire` based on it)
- `questionnaire` (`required = False`, you send it when creating a 'CXI' questionnaire)
- `entity` : *id*
- `type` : *char* ('m', or 'c')
- `section` : *id* (`null = True`)
- `employee_type` : *id* (for `ContentType`: `clientmanager` or `clientemployee`)
- `visit_type` : *string* (`choises = 'call', 'visit'`)
- `suggested_start_date` : *datetime*
- `suggested_end_date` : *datetime*
- `status` : *char* (can take these values: `PLANNED = 'planned', DRAFT = 'draft', SUBMITTED = 'submitted', REVIEWED = 'reviewed', APPROVED = 'approved', DECLINED = 'declined', REJECTED = 'rejected'`)
- `time_accomplished` : *datetime* (`required = False)
- `shopper` : *id*
- `evaluation_assessment_level` : *id* (at first is null)

> example:
```json
{
    "questionnaire": {...},
    "type": null,
    "employee_id": null,
    "evaluation_type": null,
    "is_draft": false,
    "suggested_start_date": null,
    "suggested_end_date": null,
    "status": null,
    "time_accomplished": null,
    "project": null,
    "shopper": null,
    "questionnaire_script": null,
    "questionnaire_template": null,
    "entity": null,
    "section": null,
    "employee_type": null,
    "evaluation_assessment_level": null
}
```

**`GET`**:

- `id` : *int*
- `shopper_repr` : *represenation* of `Shopper`
- `project` : *id*
- `shopper` : *id*
- `questionnaire_script` : *id*
- `questionnaire_script_repr` : *representation*
- `questionnaire_template` : *id* (it will take this `questionnaire template` and create a `questionnaire` based on it)
- `questionnaire` (`required = False`, you send it when creating a 'CXI' questionnaire)
- `entity` : *id*
- `type` : *char* ('m', or 'c')
- `section` : *id* (`null = True`)
- `section_repr` : *representation* of `Section`
- `employee_id`: *int*
- `employee_type` : *id* (for `ContentType`: `clientmanager` or `clientemployee`)
- `visit_type` : *string* (`choises = 'call', 'visit'`)
- `suggested_start_date` : *datetime*
- `suggested_end_date` : *datetime*
- `status` : *char* (can take these values: `PLANNED = 'planned', DRAFT = 'draft', SUBMITTED = 'submitted', REVIEWED = 'reviewed', APPROVED = 'approved', DECLINED = 'declined', REJECTED = 'rejected'`)
- `time_accomplished` : *datetime* (`required = False)
- `created` : *datetime*
- `modified` : *datetime*
- `shopper` : *id*
- `evaluation_assessment_level` : *id* (at first is null)

> [example](projects\ example/plannedevaluation.json)

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
- `evaluation` : *id*
- `questionnaire` : *id*
- `comment` : *string* (`TextField`)

> example:
```json
{
    "commenter_id": null,
    "comment": "",
    "commenter_type": null,
    "evaluation_assessment_level": null,
    "evaluation": null,
    "questionnaire": null
}
```

**`GET`**:

- `id` : *int*
- `commenter_id` : *integer*
- `commenter_type` : *id* (for `ContentType`: `tenantprojectmanager` or `tenantconsultant`)
- `evaluation_assessment_level` : *id*
- `comment` : *string* (`TextField`)
- `commenter_repr` : *representation* of `Project Manager` or `Consultant` (`read_only = True`)
- `evaluation` : *id*
- `questionnaire` : *id*

> example:
```json
{
    "id": 1,
    "commenter_repr": {
        "id": 1,
        "user": {
            "id": 1,
            "username": "mihai",
            "email": "",
            "first_name": "",
            "last_name": "",
            "roles": [
                "tenantproductmanager",
                "tenantprojectmanager",
                "admin"
            ],
            "shopper": null
        },
        "tenant_repr": {
            "id": 1,
            "name": "SparkLabs"
        },
        "type": "tenantproductmanager",
        "tenant": 1
    },
    "commenter_id": 1,
    "comment": "This is a comment",
    "commenter_type": 14,
    "evaluation_assessment_level": 1,
    "evaluation": 1,
    "questionnaire": 1
}
```
