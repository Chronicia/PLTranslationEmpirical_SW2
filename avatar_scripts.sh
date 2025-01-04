#!/usr/bin/env bash

# Translation
bash scripts/translate.sh gpt-4o-mini avatar Java C++ 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Java Go 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Java C 50 0.95 0.7 0
bash scripts/translate.sh gpt-4o-mini avatar Java Python 50 0.95 0.7 0

# Generate Report
bash scripts/test_avatar.sh Java C++ gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java Go gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java C gpt-4o-mini fix_reports 1
bash scripts/test_avatar.sh Java Python gpt-4o-mini fix_reports 1

# Repair compile (fix1)
bash scripts/repair.sh gpt-4o-mini avatar Java C++ 50 0.95 0.7 0 1 compile 20241225_183200 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Go 50 0.95 0.7 0 1 compile 20241225_183502 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java C 50 0.95 0.7 0 1 compile 20241225_184533 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Python 50 0.95 0.7 0 1 compile 20241225_184831 {timestamp of the fix report}

# Report fix1
cd output && cp -r gpt-4o-mini_IO_1/avatar/Java/C++/* gpt-4o-mini/avatar/Java/C++ && cd ..
bash scripts/test_avatar.sh Java C++ gpt-4o-mini fix_reports 2

cd output && cp -r gpt-4o-mini_IO_1/avatar/Java/Go/* gpt-4o-mini/avatar/Java/Go && cd ..
bash scripts/test_avatar.sh Java Go gpt-4o-mini fix_reports 2

cd output && cp -r gpt-4o-mini_IO_1/avatar/Java/C/* gpt-4o-mini/avatar/Java/C && cd ..
bash scripts/test_avatar.sh Java C gpt-4o-mini fix_reports 2

cd output && cp -r gpt-4o-mini_IO_1/avatar/Java/Python/* gpt-4o-mini/avatar/Java/Python && cd ..
bash scripts/test_avatar.sh Java Python gpt-4o-mini fix_reports 2

# Repair runtime (fix2)
bash scripts/repair.sh gpt-4o-mini avatar Java C++ 50 0.95 0.7 0 2 runtime 20241225_232928 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Go 50 0.95 0.7 0 2 runtime 20241225_233405 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java C 50 0.95 0.7 0 2 runtime 20241225_233813 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Python 50 0.95 0.7 0 2 runtime 20241225_233839 {timestamp of the fix report}

# Report fix2
cd output && cp -r gpt-4o-mini_IO_2/avatar/Java/C++/* gpt-4o-mini/avatar/Java/C++ && cd ..
bash scripts/test_avatar.sh Java C++ gpt-4o-mini fix_reports 3

cd output && cp -r gpt-4o-mini_IO_2/avatar/Java/Go/* gpt-4o-mini/avatar/Java/Go && cd ..
bash scripts/test_avatar.sh Java Go gpt-4o-mini fix_reports 3

cd output && cp -r gpt-4o-mini_IO_2/avatar/Java/C/* gpt-4o-mini/avatar/Java/C && cd ..
bash scripts/test_avatar.sh Java C gpt-4o-mini fix_reports 3

cd output && cp -r gpt-4o-mini_IO_2/avatar/Java/Python/* gpt-4o-mini/avatar/Java/Python && cd ..
bash scripts/test_avatar.sh Java Python gpt-4o-mini fix_reports 3

# Repair incorrect (fix3)
bash scripts/repair.sh gpt-4o-mini avatar Java C++ 50 0.95 0.7 0 3 incorrect 20241226_021007 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Go 50 0.95 0.7 0 3 incorrect 20241226_021046 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java C 50 0.95 0.7 0 3 incorrect 20241226_021241 {timestamp of the fix report}
bash scripts/repair.sh gpt-4o-mini avatar Java Python 50 0.95 0.7 0 3 incorrect 20241226_021357 {timestamp of the fix report}

# Report fix3
cd output && cp -r gpt-4o-mini_IO_3/avatar/Java/C++/* gpt-4o-mini/avatar/Java/C++ && cd ..
bash scripts/test_avatar.sh Java C++ gpt-4o-mini fix_reports 4

cd output && cp -r gpt-4o-mini_IO_3/avatar/Java/Go/* gpt-4o-mini/avatar/Java/Go && cd ..
bash scripts/test_avatar.sh Java Go gpt-4o-mini fix_reports 4

cd output && cp -r gpt-4o-mini_IO_3/avatar/Java/C/* gpt-4o-mini/avatar/Java/C && cd ..
bash scripts/test_avatar.sh Java C gpt-4o-mini fix_reports 4

cd output && cp -r gpt-4o-mini_IO_3/avatar/Java/Python/* gpt-4o-mini/avatar/Java/Python && cd ..
bash scripts/test_avatar.sh Java Python gpt-4o-mini fix_reports 4