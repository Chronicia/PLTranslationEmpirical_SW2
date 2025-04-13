WORKDIR=`pwd`
export PYTHONPATH=$WORKDIR;
export PYTHONIOENCODING=utf-8;

function prompt() {
    echo;
    echo "Syntax: bash scripts/translate.sh MODEL DATASET SRC_LANG TRG_LANG K P TEMPERATURE GPU_ID [MODE]";
    echo "MODEL: name of the model to use";
    echo "DATASET: name of the dataset to use";
    echo "SRC_LANG: source language";
    echo "TRG_LANG: target language";
    echo "K: top-k sampling";
    echo "P: top-p sampling";
    echo "TEMPERATURE: temperature for sampling";
    echo "GPU_ID: GPU to use";
    echo "MODE: (optional) mode for translation";
    exit;
}

while getopts ":h" option; do
    case $option in
        h) # display help
          prompt;
    esac
done

# Check if at least 8 arguments are provided
if [[ $# -lt 8 ]]; then
  prompt;
fi

MODEL=$1;
DATASET=$2;
SRC_LANG=$3;
TRG_LANG=$4;
K=$5;
P=$6;
TEMPERATURE=$7;
GPU_ID=$8;
MODE=${9:-"direct"};  # Set MODE to "direct" if not provided

python3 src/translation/translate_gpt_parallel.py --model $MODEL --dataset $DATASET --source_lang $SRC_LANG --target_lang $TRG_LANG --k $K --p $P --temperature $TEMPERATURE --mode $MODE;
