PY ?= /_work/_tool/Python/3.7.7/x64/bin/python3.7
export PY

VENVDIR?=$(WORKDIR)/venv/test
export VENVDIR

ifeq ($(APP),)
$(error APP is not set)
endif

ifeq ($(BROWSER_NAME),)
	BROWSER_NAME := Chrome
endif

BROWSER_NAME_FOLDER := $(shell echo "$(BROWSER_NAME)" | tr A-Z a-z)

ifeq ($(BROWSER_VER),)
	BROWSER_VER_PARAM := 
else
	BROWSER_VER_PARAM := -D browserver=$(BROWSER_VER) 
endif

ifeq ($(PROC_NUM),)
	PROC_NUM_PARAM := 
else
	PROC_NUM_PARAM := -p $(PROC_NUM) 
endif

ifeq ($(LT_USER),)
$(error LT_USER is not set)
endif

ifeq ($(LT_ACCESS_KEY),)
$(error LT_ACCESS_KEY is not set)
endif

ifeq ($(TEST_TAG),)
$(error TEST_TAG is not set)
else
	comma := ,
	ifeq ($(findstring $(comma),$(TEST_TAG)),$(comma))
	TAG_NAME := custom
	else
	TAG_NAME := $(shell echo "$(TEST_TAG)" | cut -c 2-)
	endif
endif


REPORT_DIR := /_work/reports/$(APP)/$(BROWSER_NAME_FOLDER)/$(TAG_NAME)
UI_FEATURES_DIR := ./tests/UI/features

BUILD_NAME := $(TAG_NAME)_$(shell date +"%Y%m%d%H%M")

.PHONY: setup-req
setup-req: venv
	$(VENV)/pip install --upgrade -r requirements.txt
	cp config.example.ini config.ini

.PHONY: setup-tunnel
setup-tunnel:
	chmod 777 ./LT && nohup ./LT --user $(LT_USER) --key $(LT_ACCESS_KEY) -tunnelName $(TUNNEL_NAME) &

.PHONY: clear-logs
clear-logs: 
	rm -rf /_work/logs/allure_report
	rm -rf $(UI_FEATURES_DIR)/parallel/ || true

.PHONY: run-tests
run-tests: venv
	${MAKE} clear-logs
	$(VENV)/behave --no-skipped \
	-D lt_username=$(LT_USER) \
	-D lt_access_key=$(LT_ACCESS_KEY) \
	-D lt_tunnel=$(TUNNEL_NAME) \
	-D build_id="$(BUILD_NAME)" \
	-f allure -o /_work/logs/allure_report \
	-e par_.* \
	--tags=$(TEST_TAG) $(UI_FEATURES_DIR)

.PHONY: parallel-test
parallel-test: venv
	${MAKE} clear-logs
	
	$(VENV)/python ./parallel_runner.py split \
	-fd $(UI_FEATURES_DIR) \
	--tags=$(TEST_TAG) \
	-res $(UI_FEATURES_DIR)/parallel/
	
	$(VENV)/python ./parallel_runner.py  run \
	-fd $(UI_FEATURES_DIR)/parallel/ \
	--venv=$(VENV) --no-skipped --no-capture \
	-D lt_username=$(LT_USER) \
	-D lt_access_key=$(LT_ACCESS_KEY) \
	-D lt_tunnel=$(TUNNEL_NAME) \
	-D build_id=$(BUILD_NAME) \
	-D browsername=$(BROWSER_NAME) \
	$(BROWSER_VER_PARAM) \
	$(PROC_NUM_PARAM) \
	-f allure -o /_work/logs/allure_report \
	--tags=$(TEST_TAG)

.PHONY: gen-reports
gen-reports:
	$(eval LAST_BUILD := $(shell cd $(REPORT_DIR) && ls -td -- */ | head -n 1 | cut -d'/' -f1))
	@echo "$(LAST_BUILD)"
	if [ -d "$(REPORT_DIR)" ]; then \
		echo "report dir is $(REPORT_DIR)"; \
		if [ -d "$(REPORT_DIR)/$(LAST_BUILD)" ]; then \
			echo "last build dir is $(REPORT_DIR)/$(LAST_BUILD)"; \
			if [ "$(TAG_NAME)" != "custom" ]; then \
				mkdir -p /_work/logs/allure_report/history; \
				cp -r $(REPORT_DIR)/$(LAST_BUILD)/history/* /_work/logs/allure_report/history/; \
				echo "History copied successfully"; \
			fi \
		fi \
	else \
		echo "REPORT_DIR not found"; \
	fi

	allure generate -c /_work/logs/allure_report -o $(REPORT_DIR)/$(BUILD_NAME)

.PHONY: kill-tunnel
kill-tunnel: 
	kill -9 $(shell pgrep -f LT)

include Makefile.venv
