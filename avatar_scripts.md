# AVATAR Benchmark Scripts
## From Java
Translation
```bash
bash scripts/translate.sh gpt-4o-mini avatar Java C++ 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Java Go 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Java C 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Java Python 50 0.95 0.7 0
```
Generate Report
```bash
bash scripts/test_avatar.sh Java C++ gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java Go gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java C gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java Python gpt-4o-mini fix_reports 1
```

Repairing Unsuccessful Translations
```bash
bash scripts/repair.sh gpt-4o-mini avatar C++ Java 50 0.95 0.7 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Go Java 50 0.95 0.7 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar C Java 50 0.95 0.7 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Python Java 50 0.95 0.7 0 1 compile {timestamp of the fix report}
```
  


## From Python
```bash
bash scripts/translate.sh gpt-4o-mini avatar Python C++ 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Python Go 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Python Java 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Python C 50 0.95 0.7 0
```
Generate Report
```bash
bash scripts/test_avatar.sh Python C++ gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Python Go gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Python Java gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Python C gpt-4o-mini fix_reports 1
```

Repairing Unsuccessful Translations
```bash
bash scripts/repair.sh gpt-4o-mini avatar Python C++ 50 0.95 0.7 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Python Go 50 0.95 0.7 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Python Java 50 0.95 0.7 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Python C 50 0.95 0.7 0 1 compile {timestamp of the fix report}
```
