# Domain Data Validation Report

Overall: **PASS**

| Result | Rule | Detail |
|---|---|---|
| PASS | table row counts | all counts match scenario |
| PASS | required columns | no null/empty required values |
| PASS | primary keys | all primary keys unique |
| PASS | unique constraints | all configured unique keys unique |
| PASS | physical and logical foreign keys | all references resolve |
| PASS | hotspot course ratio | actual=200, expected=200 |
| PASS | course time range | all times valid and aligned to 30 minutes |
| PASS | prerequisite satisfiability | every rule is satisfiable by a student in its department |
| PASS | course current_count | matches baseline enrollments |
