# Objective 5, Step 5: accessibility scan

Scanner: axe-core. Rule: no serious or critical issue.

- lab: 7 states, 10 keyboard stops
- kiosk: 2 states, 2 keyboard stops

**Serious or critical issues: 0** -> met

| Mode | State | Impact | Rule | Element | Detail |
|---|---|---|---|---|---|
| lab | welcome | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
| lab | after a shopping turn (cards, quick replies) | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
| lab | tool-call drawer | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
| lab | stage drawer | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
| lab | pipeline menu open | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
| lab | Custom switches, untested banner | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
| lab | compare mode after a turn | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
| kiosk | welcome | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
| kiosk | after a shopping turn (cards, quick replies) | moderate | page-has-heading-one | `html` | Page should contain a level-one heading |
