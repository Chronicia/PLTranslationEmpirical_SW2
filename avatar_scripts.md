# AVATAR Benchmark Scripts
## From Java
Translation
```bash
bash scripts/translate.sh gpt-4o-mini avatar Java C++ 50 1.0 0.3 0
bash scripts/translate.sh gpt-4o-mini avatar Java Go 50 1.0 0.3 0
bash scripts/translate.sh gpt-4o-mini avatar Java C 50 1.0 0.3 0
bash scripts/translate.sh gpt-4o-mini avatar Java Python 50 1.0 0.3 0
```
Generate Report
```bash
bash scripts/test_avatar.sh Java C++ gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java Go gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java C gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java Python gpt-4o-mini fix_reports 1
```

Repairing Unsuccessful Translations (fix1 use "compile". Always run "Generate Report after repair" before continuing new fixes. Then fix2 use "runtime", fix3 use "incorrect")
```bash
# Repair compile (fix1)
bash scripts/repair.sh gpt-4o-mini avatar Java C++ 50 1.0 0.3 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Go 50 1.0 0.3 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java C 50 1.0 0.3 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Python 50 1.0 0.3 0 1 compile {timestamp of the fix report}

# Repair runtime (fix2)
bash scripts/repair.sh gpt-4o-mini avatar Java C++ 50 1.0 0.3 0 2 runtime {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Go 50 1.0 0.3 0 2 runtime {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java C 50 1.0 0.3 0 2 runtime {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Python 50 1.0 0.3 0 2 runtime {timestamp of the fix report}

# Repair incorrect (fix3)
bash scripts/repair.sh gpt-4o-mini avatar Java C++ 50 1.0 0.3 0 3 incorrect {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Go 50 1.0 0.3 0 3 incorrect {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java C 50 1.0 0.3 0 3 incorrect {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Python 50 1.0 0.3 0 3 incorrect {timestamp of the fix report}
```

Generate Report after repair (Change "_IO_[n]" to the directory that contain new fixed files)
```bash
cd output && cp -r gpt-4o-mini_IO_[n]/avatar/Java/C++/* gpt-4o-mini/avatar/Java/C++ && cd ..
bash scripts/test_avatar.sh Java C++ gpt-4o-mini fix_reports [n+1]

cd output && cp -r gpt-4o-mini_IO_[n]/avatar/Java/Go/* gpt-4o-mini/avatar/Java/Go && cd ..
bash scripts/test_avatar.sh Java Go gpt-4o-mini fix_reports [n+1]

cd output && cp -r gpt-4o-mini_IO_[n]/avatar/Java/C/* gpt-4o-mini/avatar/Java/C && cd ..
bash scripts/test_avatar.sh Java C gpt-4o-mini fix_reports [n+1]

cd output && cp -r gpt-4o-mini_IO_[n]/avatar/Java/Python/* gpt-4o-mini/avatar/Java/Python && cd ..
bash scripts/test_avatar.sh Java Python gpt-4o-mini fix_reports [n+1]
```


## From Python
```bash
bash scripts/translate.sh gpt-4o-mini avatar Python C++ 50 1.0 0.3 0
bash scripts/translate.sh gpt-4o-mini avatar Python Go 50 1.0 0.3 0
bash scripts/translate.sh gpt-4o-mini avatar Python Java 50 1.0 0.3 0
bash scripts/translate.sh gpt-4o-mini avatar Python C 50 1.0 0.3 0
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
bash scripts/repair.sh gpt-4o-mini avatar Python C++ 50 1.0 0.3 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Python Go 50 1.0 0.3 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Python Java 50 1.0 0.3 0 1 compile {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Python C 50 1.0 0.3 0 1 compile {timestamp of the fix report}
```
