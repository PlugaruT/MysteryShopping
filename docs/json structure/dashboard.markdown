## Dashboard Template

#### `structure`
- `x`, `y`: top-left corner coordinates for the dashboard card
- `width`, `height`: number of `cells` horizontally and vertically, respectively
- `type` : type of card content (`text`/`chart`/`...`)
- `options` : will contain additional information about the `type` of card content
	- `type` : (for `chart`) can be `bar`/`pie`/`timeseries`/`line`/`bullet`/`...`
	- some other fields
- `source` : **list** for `Questionnare Template Question` (for `bar` chart)
- `show_comment` : **bool** - will determine whether to create or not a `Dashboard Comment` (explanation following at the next field)
- `comment_source` : **id**. On `DashboardTemplate` `save` check whether `show_comment` is `True` and create a new `Dashboard Comment` and save its `id` in this field