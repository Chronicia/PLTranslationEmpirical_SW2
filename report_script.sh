MODEL=$1;
echo Generating $MODEL fix report
echo Generating Java to C++ report
bash scripts/test_avatar.sh Java C++ $MODEL fix_reports 1
echo Generating Java to Go report
bash scripts/test_avatar.sh Java Go $MODEL fix_reports 1
echo Generating Java to C report
bash scripts/test_avatar.sh Java C $MODEL fix_reports 1
echo Generating Java to Python report
bash scripts/test_avatar.sh Java Python $MODEL fix_reports 1

echo Generating Python to C++ report
bash scripts/test_avatar.sh Python C++ $MODEL fix_reports 1
echo Generating Python to Go report
bash scripts/test_avatar.sh Python Go $MODEL fix_reports 1
echo Generating Python to Java report
bash scripts/test_avatar.sh Python Java $MODEL fix_reports 1
echo Generating Python to C report
bash scripts/test_avatar.sh Python C $MODEL fix_reports 1
