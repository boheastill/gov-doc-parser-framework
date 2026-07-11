#!/bin/bash
# Run the parser CLI against the Data Protection Act 2018 HTML fixture
.venv/bin/python3 cli.py fixtures/irishstatutebook/data_protection_act_2018.html --source irishstatutebook.ie --url "https://www.irishstatutebook.ie/eli/2018/act/7/enacted/en/print.html" -o out.json
