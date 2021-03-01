"""
This module contains all hooks
Order of execution in Behave see below.

before_all
for feature in all_features:
    before_feature
    for outline in feature.scenarios:
        for scenario in outline.scenarios:
            before_scenario
            for step in scenario.steps:
                before_step
                    step.run()
                after_step
            after_scenario
    after_feature
after_all
"""
from allure_commons.types import AttachmentType
import allure

from utilities.config import Config
from utilities.log import Logger

from psutil import Process

import platform
import logging
import json
import os
import re


def before_all(context):
    """
    Before all hook.
    Set config variables for whole run, setup logging.
    context.config.userdata is a dict with values from behave commandline.
    Example: -D foo=bar will store value in config.userdata['foo'].
    Will be executed once at the beginning of the test run.
    Context injected automatically by Behave.
    :type context: behave.runner.Context
    """
    Logger.configure_logging()
    logger = logging.getLogger(__name__)

    if context.config.userdata:
        Config.ENV = context.config.userdata.get('env', Config.ENV)

        Config.REUSE = context.config.userdata.get('reuse', Config.REUSE)
        Config.HIGHLIGHT = context.config.userdata.get('highlight', Config.HIGHLIGHT)

        Config.BROWSERTYPE = context.config.userdata.get('browsertype', Config.BROWSERTYPE)
        Config.PLATFORM = context.config.userdata.get('osplatform', Config.PLATFORM)
        Config.BROWSERNAME = context.config.userdata.get('browsername', Config.BROWSERNAME)
        Config.VERSION = context.config.userdata.get('browserver', Config.VERSION)

        context.lt_username = context.config.userdata.get('lt_username', "ERROR_LT_USERNAME")
        context.lt_access_key = context.config.userdata.get('lt_access_key', "ERROR_LT_ACCESS_KEY")
        context.lt_tunnel = context.config.userdata.get('lt_tunnel', "ERROR_LT_TUNNEL")
        context.build = context.config.userdata.get('build_id', "ERROR_BUILD_ID")

    context.run_mode = context.config.userdata.get('behave_run_mode', "ERROR_RUN_MODE")

    # pid from parallel_runner
    if platform.system() == 'Windows':
        # On Win: pool_process -> cmd (call function) -> behave -> python -> before_all (hook)
        parent_runner_pid = Process(Process(Process(Process(os.getpid()).ppid()).ppid()).ppid()).ppid()
    elif platform.system() == 'Linux':
        # On Lin: pool_process -> behave -> before_all (hook)
        parent_runner_pid = Process(Process(os.getpid()).ppid()).ppid()
    elif platform.system() == 'Darwin':
        # On Darwin: pool_process -> behave -> before_all (hook)
        parent_runner_pid = Process(Process(os.getpid()).ppid()).ppid()

    logger.info("parent pid: " + str(parent_runner_pid))

    if context.run_mode == 'Multithreaded' and os.path.exists("pid_" + str(parent_runner_pid) + ".db"):
        with open("pid_" + str(parent_runner_pid) + ".db", "r") as context_file:
            content = context_file.read()
            variables = re.findall(r"<var_beg>(.+?)<var_end>", content)
            for var in variables:
                if "project_db" in var:
                    context.project_db = json.loads(var.replace("project_db=", '').replace("'", '"'))
    else:
        context.project_db = json.loads(Config.PROJECT_DB.replace("'", '"'))


def after_all(context):
    """
    After all hook.
    Will be executed once at the beginning of the test run.
    Context injected automatically by Behave.
    :type context: behave.runner.Context
    """
    if context.run_mode == 'Multithreaded':
        # pid from parallel_runner
        if platform.system() == 'Windows':
            # On Win: pool_process -> cmd (call function) -> behave -> python -> before_all (hook)
            parent_runner_pid = Process(Process(Process(Process(os.getpid()).ppid()).ppid()).ppid()).ppid()
        elif platform.system() == 'Linux':
            # On Lin: pool_process -> behave -> before_all (hook)
            parent_runner_pid = Process(Process(os.getpid()).ppid()).ppid()
        elif platform.system() == 'Darwin':
            # On Darwin: pool_process -> behave -> before_all (hook)
            parent_runner_pid = Process(Process(os.getpid()).ppid()).ppid()

    if context.project_db:
        logger = logging.getLogger(__name__)
        logger.info("context.project_db in this thread: " + str(context.project_db).replace("'", '"'))

        if context.run_mode == 'Multithreaded':
            with open("pid_" + str(parent_runner_pid) + ".db", "w") as context_file:
                context_file.write("<var_beg>" + "project_db=" + str(context.project_db) + "<var_end>\n")


def before_feature(context, feature):
    """
    Before feature hook.
    Will be executed for every .feature file.
    Context and feature injected automatically by Behave
    :type context: behave.runner.Context
    :type feature: behave.model.Feature
    """
    logger = logging.getLogger(__name__)

    context.browser = None


def after_feature(context, feature):
    """
    After feature hook.
    Will be executed after every .feature file.
    Context and feature injected automatically by Behave
    :type context: behave.runner.Context
    :type feature: behave.model.Feature
    """
    logger = logging.getLogger(__name__)


def before_scenario(context, scenario):
    """
    Before scenario hook.
    Create folder for screenshot, open browser, set Full HD resolution and place browser in test context.
    Will be executed in the beginning of every scenario in .feature file.
    Context and scenario injected automatically by Behave
    :type context: behave.runner.Context
    :type scenario: behave.model.Scenario
    """
    Logger.create_test_folder(scenario.name)
    logger = logging.getLogger(__name__)

    if context.browser is None:
        try:
            if Config.BROWSERTYPE == 'Local':
                if Config.BROWSERNAME == 'Chrome':
                    context.browser = Config.browser_types[Config.BROWSERNAME](chrome_options=Config.CHROME_OPTIONS)
                    context.browser.set_window_size(1920, 1080)
                if Config.BROWSERNAME == 'Firefox':
                    context.browser = Config.browser_types[Config.BROWSERNAME]()
                    context.browser.set_window_size(1920, 1080)
                if Config.BROWSERNAME == 'Edge':
                    context.browser = Config.browser_types[Config.BROWSERNAME]()
                    context.browser.set_window_size(1920, 1080)
            elif Config.BROWSERTYPE == 'Remote':
                url = "https://" + context.lt_username + ":" + context.lt_access_key + "@hub.lambdatest.com/wd/hub"
                desired_cap = {
                    "platform": Config.PLATFORM,
                    "browserName": Config.BROWSERNAME,
                    "version": Config.VERSION,
                    "resolution": "1920x1080",
                    "name": scenario.name,
                    "build": context.build,
                    "tunnel": True,
                    "tunnelName": context.lt_tunnel,
                    "console": True,
                    "network": False,
                    "visual": True
                }
                context.browser = Config.browser_types[Config.BROWSERTYPE](
                    desired_capabilities=desired_cap,
                    command_executor=url
                )
            else:
                print('Wrong type of browser')
        except Exception:
            logger.error(
                'Failed to start browser: {}'.format(Config.BROWSERNAME))
            raise

    logger.info('Start of test: {}'.format(scenario.name))


def after_scenario(context, scenario):
    """
    After scenario hook.
    Close browser in case it don't needed anymore.
    Make screenshot when test result = failed.
    Will be executed after every scenario in .feature file.
    Context and scenario injected automatically by Behave
    :type context: behave.runner.Context
    :type scenario: behave.model.Scenario
    """
    logger = logging.getLogger(__name__)

    if scenario.status == 'failed':
        _screenshot = '{}/{}/__Fail.png'.format(Config.LOG_DIR, scenario.name.replace(' ', '_'))

        try:
            context.browser.save_screenshot(_screenshot)
        except Exception:
            logger.error(
                'Failed to take screenshot to: {}'.format(Config.LOG_DIR))
            raise

        try:
            with open(_screenshot, 'rb') as _file:
                allure.attach(_file.read(), '{} fail'.format(scenario.name), AttachmentType.PNG)
        except Exception:
            logger.error(
                'Failed to attach to report screenshot: {}'.format(_screenshot))
            raise

    if Config.BROWSERTYPE == 'Remote':
        if scenario.status == 'failed':
            context.browser.execute_script('lambda-status=failed')

        if scenario.status == 'passed':
            context.browser.execute_script('lambda-status=passed')

    if not Config.REUSE:
        try:
            context.browser.quit()
        except Exception:
            logger.error(
                'Failed to close browser: {}'.format(Config.BROWSERNAME))
            raise

        context.browser = None

    logger.info('End of test: {}. Status: {} !!!\n\n\n'.format(scenario.name, scenario.status))


def before_step(context, step):
    """
    Before step hook.
    Will be executed before every test step.
    Context and step injected automatically by Behave
    :type context: behave.runner.Context
    :type step: behave.model.Step
    """
    logger = logging.getLogger(__name__)


def after_step(context, step):
    """
    After step hook.
    Context and step injected automatically by Behave
    :type context: behave.runner.Context
    :type step: behave.model.Step
    """
    logger = logging.getLogger(__name__)

    if step.status.name == 'failed':  # get last traceback and error message
        context.last_traceback = step.error_message
        if step.error_message is not None:
            try:
                context.last_error_message = step.error_message.split('ERROR:')[1]
            except IndexError:
                context.last_error_message = step.error_message
