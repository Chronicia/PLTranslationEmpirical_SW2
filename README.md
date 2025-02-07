# Lost in Translation: A Study of Bugs Introduced by Large Language Models while Translating Code

### To-do List
- [x] Update README:
  - [x] Instructions for install repo, dependencies
  - [x] Download artifacts and datasets
  - [x] Run translation and benchmark
  - [x] Put unimportant things in the end 
- [x] Change requirements.txt to openai-api 1.0+
- [x] Migrate [translations.py](http://translations.py) to openai-api 1.0+
- [x] Make translation output with Azure GPT-4o-mini
- [ ] Benchmark accuracy of output codes

### Install
Download conda (miniconda/condaforge). Afterwards run this:
```
git clone https://github.com/Intelligent-CAT-Lab/PLTranslationEmpirical
conda create -n plempirical python=3.10.13
conda activate plempirical
python3 --version && pip3 --version
pip3 install -r requirements.txt
```
Download both `dataset.zip` and `artifacts.zip` from [Zenodo](https://zenodo.org/doi/10.5281/zenodo.8190051) repository

### Dependencies
**Software dependencies**: (1) in requirements.txt, (2) compilers for PLs: g++ 11, GCC Clang 14.0, Java 11, Go 1.20, Rust 1.73, and .Net 7.0.14 for Python, C++, C, Java, Go, Rust, and C#.

**Hardware dependencies**: 16 NVIDIA A100 GPUs, 80GBs memory each for inferencing models. Memory need to be enough so that all model weights can be loaded into memory.

**To run scripts of non-LLM Methods**: install [C2Rust](https://github.com/immunant/c2rust), [CxGO](https://github.com/gotranspile/cxgo), and [Java2C#](https://github.com/paulirwin/JavaToCSharp). Please refer to their repositories for installation instructions. For Java2C#, you need to create a `.csproj` file like below:
```
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net7.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

</Project>
```

### Dataset
`dataset.zip` includes:

1. [CodeNet](https://github.com/IBM/Project_CodeNet)
2. [AVATAR](https://github.com/wasiahmad/AVATAR)
3. [Evalplus](https://github.com/evalplus/evalplus)
4. [Apache Commons-CLI](https://github.com/apache/commons-cli)
5. [Click](https://github.com/pallets/click)

dataset directory structure:
```
PLTranslationEmpirical
├── dataset
    ├── codenet
    ├── avatar
    ├── evalplus
    ├── real-life-cli
├── ...
```

The structure of each dataset is as follows:

1. CodeNet & Avatar: `/SRC_LANG/Code, TestCases`. Each code snippet has an `id` in the filename, which is the same in both `Code` and `TestCases`.

2. Evalplus: The source language code snippets follow a similar structure as CodeNet and Avatar. However, as a one time effort, we manually created the test cases in the target Java language inside a maven project, `evalplus_java`. To evaluate the translations from an LLM, we recommend moving the generated Java code snippets to the `src/main/java` directory of the maven project and then running the command `mvn clean test surefire-report:report -Dmaven.test.failure.ignore=true` to compile, test, and generate reports for the translations.

3. Real-life Projects: The `real-life-cli` directory represents two real-life CLI projects from Java and Python. These datasets only contain code snippets as files and no test cases. As mentioned in the paper, the authors manually evaluated the translations for these datasets.

### Scripts
Create a `.env` file in the repository and add the following:

```
AZURE_OPENAI_ENDPOINT=
CHATBOT_API_KEY=<your openai api key>
LLAMA2_AUTH_TOKEN=<your llama2 auth token from huggingface>
STARCODER_AUTH_TOKEN=<your starcoder auth token from huggingface>
```

#### 1. Hyperparameters
Here are the default parameter values, which yield the result we get. For reproducibility, please stick to the default values. For experimentation, feel free to alter the values as you see fit. 

- `$DATASET`= {avatar, codenet, evalplus, real-life-cli}
- `$MODEL`= {gpt-4o-mini, gpt-4o, gpt-4, gemini-1.5-pro-001, gemini-1.5-flash-001, gemini-1.5-pro-002, 
 StarCoder, CodeGen}
- `$SRC_LANG`, `$TRG_LANG`= {C, C++, Go, Java, Python} (if `$DATASET` = codenet), {Java, Python} (`$DATASET` = {avatar, evalplus, real-life-cli}), {Rust} (`$MODEL`=C2Rust), {C#} (`$MODEL`=Java2C#)
- `$K`=50 (top-k sampling)
- `$P`=0.95 (top-p sampling)
- `$TEMP`=0.7
- `$GPU_ID`=0


#### 2. Translation (Refer to `scripts\translate.sh`)

2.1. `$MODEL` = {gpt-4o, gpt-4o-mini, gemini-1.5-pro-001, gemini-1.5-flash-001, gemini-1.5-pro-002}
```
bash scripts/translate.sh $MODEL $DATASET $SRC_LANG $TRG_LANG $K $P $TEMP=0.7 $GPU_ID
```

2.2. `$MODEL` = {CodeGeeX}

Clone CodeGeeX repository: https://github.com/THUDM/CodeGeeX , use instructions from their artifacts to download model weights. After cloning it inside `PLTranslationEmpirical` and downloading the model weights, your directory structure should be like the following:

```
PLTranslationEmpirical
├── dataset
    ├── codenet
    ├── avatar
    ├── evalplus
    ├── real-life-cli
├── CodeGeeX
    ├── codegeex
    ├── codegeex_13b.pt # this file is the model weight
    ├── ...
├── ...
```
Script:
```
bash scripts/translate.sh CodeGeeX $DATASET $SRC_LANG $TRG_LANG $K $P $TEMP=0.2 $GPU_ID
```

2.3. `$MODEL` = {StarCoder, CodeGen, and others}.

Translate `Python -> Java`, dataset `codenet`, top-k sampling `k=50`, top-p sampling `p=0.95`, `temperature=0.2`, on GPU `gpu_id=0`:
```
bash scripts/translate.sh $MODEL $DATASET $SRC_LANG $TRG_LANG $K $P $TEMP=0.2 $GPU_ID
```

2.4. Traditional techniques (i.e., C2Rust, CxGO, Java2C#):
```
bash scripts/translate_transpiler.sh codenet C Rust c2rust fix_report
bash scripts/translate_transpiler.sh codenet C Go cxgo fix_reports
bash scripts/translate_transpiler.sh codenet Java C# java2c# fix_reports
bash scripts/translate_transpiler.sh avatar Java C# java2c# fix_reports
```

#### 3. Compile, test, generate fix reports  (Refer to `scripts/test_$DATASET.sh`)
`$DATASET` = {codenet, avatar, evalplus}. 

`$ATTEMPT`: Does not really matter if you keep track of `$TIMESTAMP` in `fix_reports/`. Can choose `$ATTEMPT`=0 by default.
```
bash scripts/test_avatar.sh $SRC_LANG $TRG_LANG $MODEL $OUTPUT_DIR=fix_reports $ATTEMPT
bash scripts/test_codenet.sh $SRC_LANG $TRG_LANG $MODEL $OUTPUT_DIR=fix_reports $ATTEMPT
bash scripts/test_evalplus.sh $SRC_LANG $TRG_LANG $MODEL $OUTPUT_DIR=fix_reports $ATTEMPT
```

#### 4. Repair (Refer to `scripts/repair.sh`)
`$ERROR_TYPE`= {compile, runtime, incorrect}. Check `fix_reports/` to fill in `$TIMESTAMP` and `$ATTEMPT`, since the data needed for repair procedure (error types, error files) lies within the fix reports.
```
bash scripts/repair.sh $MODEL $DATASET $SRC_LANG $TRG_LANG $K $P $TEMP $GPU_ID $ATTEMPT $ERROR_TYPE $TIMESTAMP
```

#### 5. Clean translations of open-source LLMs (i.e., StarCoder) 

```
bash scripts/clean_generations.sh $MODEL $DATASET
```

Refer to [`/prompts`](/prompts/README.md) for different vanilla and repair prompts used in our study.

### Artifacts
Brief content:
1. RQ1 - Translations: Translation files from all LLMs for all datasets. (.xlsx) Breakdown of translation results.
2. RQ2 - Manual Labeling: (.xlsx) Manual labeling results for all translation bugs.
3. RQ3 - Alternative Approaches: Translation files from all alternative approaches (i.e. C2Rust, CxGO, Java2C#). (.xlsx) Breakdown of the translation results.
4. RQ4 - Mitigating Translation Bugs: Fix results of GPT-4, StarCoder, CodeGen, and Llama 2. (.xlsx) Breakdown of the fix results.

### Contact
We look forward to hearing your feedback. Please contact [Rangeet Pan](mailto:rangeet.pan@ibm.com) or [Ali Reza Ibrahimzada](mailto:alirezai@illinois.edu) for any questions or comments 🙏.

<img padding="10" align="right" src="https://www.acm.org/binaries/content/gallery/acm/publications/artifact-review-v1_1-badges/artifacts_evaluated_reusable_v1_1.png" alt="ACM Artifacts Evaluated - Reusable v1.1" width="114" height="113"/>
<img padding="10" align="right" src="https://www.acm.org/binaries/content/gallery/acm/publications/artifact-review-v1_1-badges/artifacts_available_v1_1.png" alt="ACM Artifacts Available v1.1" width="114" height="113"/>

[![Preprint](https://img.shields.io/badge/read-preprint-blue)](http://arxiv.org/abs/2308.03109)
[![Install](https://img.shields.io/badge/install-instructions-blue)](README.md#install)
[![Dependencies](https://img.shields.io/badge/install-dependencies-blue)](README.md#dependencies)
[![Scripts](https://img.shields.io/badge/run-scripts-blue)](README.md#scripts)
[![Artifacts](https://img.shields.io/badge/check-artifacts-blue)](README.md#artifacts)
[![GitHub](https://img.shields.io/github/license/Intelligent-CAT-Lab/PLTranslationEmpirical?color=blue)](LICENSE)
[![Data](https://zenodo.org/badge/DOI/10.5281/zenodo.8190051.svg)](https://zenodo.org/doi/10.5281/zenodo.8190051)

Artifact repository for the paper [_Lost in Translation: A Study of Bugs Introduced by Large Language Models while Translating Code_](http://arxiv.org/abs/2308.03109), accepted at _ICSE 2024_, Lisbon, Portugal.
Authors are [Rangeet Pan][rangeet]* [Ali Reza Ibrahimzada][ali]*, [Rahul Krishna][rahul], Divya Sankar, Lambert Pougeum Wassi, Michele Merler, Boris Sobolev, Raju Pavuluri, Saurabh Sinha, and [Reyhaneh Jabbarvand][reyhaneh].

[rangeet]: https://rangeetpan.github.io/
[ali]: https://alirezai.cs.illinois.edu/
[rahul]: http://rkrsn.us/
[reyhaneh]: https://reyhaneh.cs.illinois.edu/index.htm

Code Lingua Leaderboard: https://codetlingua.github.io