MODEL=$1;
MODE=$2;
echo Translate uisng $MODEL
echo Translating from Java to C++
bash scripts/translate.sh $MODEL avatar Java C++ 50 1.0 0.7 0 $MODE
echo Translating from Java to Go
bash scripts/translate.sh $MODEL avatar Java Go 50 1.0 0.7 0 $MODE
echo Translating from Java to C
bash scripts/translate.sh $MODEL avatar Java C 50 1.0 0.7 0 $MODE
echo Translating from Java to Python
bash scripts/translate.sh $MODEL avatar Java Python 50 1.0 0.7 0 $MODE

echo Translating from Python to C++
bash scripts/translate.sh $MODEL avatar Python C++ 50 1.0 0.7 0 $MODE
echo Translating from Python to Go
bash scripts/translate.sh $MODEL avatar Python Go 50 1.0 0.7 0 $MODE
echo Translating from Python to Java
bash scripts/translate.sh $MODEL avatar Python Java 50 1.0 0.7 0 $MODE
echo Translating from Python to C
bash scripts/translate.sh $MODEL avatar Python C 50 1.0 0.7 0 $MODE