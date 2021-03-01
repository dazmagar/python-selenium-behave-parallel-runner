## Pre-requisites
1. Code Editor such as VSCode https://code.visualstudio.com/
2. Latest version of python https://www.python.org/downloads/
3. Latest version of chromedriver https://chromedriver.chromium.org/downloads

## Virtual Environment Setup
1. Run `pip install virtualenv`
2. Run `python -m venv venv/your_env`
3. Activate the virtual environment : `.\your_venv\Scripts\activate`
> To deactivate simply run `deactivate`
4. Replace `config.example.ini` with your modified `config.ini`

## Requirements Setup
After the virtual environment has been setup;
1. Run `pip install -r requirements.txt` This should download and add all dependencies from requirements.txt file.

## Run cases
### Local
1. Run `behave --no-capture filename.feature` or `behave --no-capture --tags=@<tagName> filename.feature`
2. Run `behave -f plain --no-capture filename.feature` to print logs from print statements.
3. Run `behave -f plain --no-capture --tags=@<tagName> filename.feature` to print logs and run specific tests by providing tag.
### Remote
1. Run `behave -D lt_username=$(lt_user) -D lt_access_key=$(lt_access_key) \`
        `-D browser=Remote -D browsername=Chrome -D browserver=83.0 \`
        `-D osplatform=Windows 10 --no-capture \`
        `-f allure -o ./logs/allure_report ./tests/features`
        also remote browser parameters can be specified in config.ini (section [REMOTE])
### Parallel
1. Run `parallel_runner.py split -fd ./tests/UI/features -f <feature_file_name>, <feature_file_name> -res ./tests/UI/features/parallel` for example to split feature into multiple files.
2. Run `parallel_runner.py run --no-skipped -fd tests/UI/features/parallel -f allure -o <allure_result_folder> --tags=@<tagName>` for example to run the tests from splitted files in diferent processes.
3. To understand additional params allowed to use, run `parallel_runner.py split --help` or `parallel_runner.py run --help`

## Generate Reports
1. Run `behave -f allure -o <allure_result_folder> .\tests\*\features\*.feature` to run tests and generate json file in the output folder.
2. Run `allure serve <allure_result_folder>` will generate the report.
