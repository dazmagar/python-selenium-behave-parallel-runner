from random import randint
from pathlib import Path
from prettytable import PrettyTable
from multiprocessing import Pool
from functools import partial
from subprocess import call
from glob import glob


import logging
import click
import time
import re
import os
import sys


logging.basicConfig(level=logging.INFO, format="[%(levelname)-8s %(asctime)s] %(message)s")
logger = logging.getLogger(__name__)

tag_regexp = re.compile("@[0-9aA-zZ\-_]+")
feature_regexp = re.compile(".*\n?Feature.+")
case_regexp = re.compile("(.+@.+\n[^#\n]+Scenario.+\n(.+[Given|When|Then|And|#].+\n)+.+)")


@click.group()
@click.pass_context
def main(context):
    '''
    The program was created in order to provide parallel execution of cases, despite the fact that behave does not support this.
    Standard work algorithm:\n
    1) split cases by files using the "split" or "splitbygroups" command \n
    2) run the cases using the "run" command \n\n

    _____  \n
    Authors:\n
        Danil Manmarev \n
        Dmitriy Sherstianikh \n
        Dmitriy Basov \n

    :)
    '''
    pass


@main.command(short_help='split cases to files with one case only (cases with a sequential tag will be in the first file)')
@click.option('--features-dir', '-fd', "features_dir", default='./', type=str, show_default=True, help='source features directory')
@click.option('--result-file-path', '-res', "result_dir", default='./', type=str, show_default=True, help='direcotry you want to save splitted files result')
@click.option('--sequence-tag', '-st', 'sequence_tag', type=str, default='@serial', show_default=True, help='tag to find and join dependent cases behind')
@click.option('--tags', '-t', 'tags', type=str, help='tags of needed cases [don`t works for behave tags expressions]')
def split(features_dir, result_dir, sequence_tag, tags):

    Path(result_dir).mkdir(parents=True, exist_ok=True)

    features_list = [os.path.normpath(feature_path) for feature_path in glob(features_dir + '/*.feature')]
    tags_list = tags.replace(' ', '').split(',')

    featureHeader_by_file = {}

    feature_files_paths = []
    result_files_with_counters = {}
    logger.info('Creating files...')
    for feature_file in features_list:
        # get all tags
        feature_content = open(feature_file, 'r').read()
        tags_in_feature = set(tag_regexp.findall(feature_content))
        if tags_in_feature.intersection(tags_list):
            # get filename part by format like 'par_<feature_name>_<num>
            filename_head = os.path.normpath(result_dir + '/' + "par_" + os.path.splitext(os.path.basename(feature_file))[0] + '_')
            feature_files_paths.append((feature_file, filename_head))
            # get feature head with tags ond Feature name
            feature_head_with_tags = feature_regexp.match(feature_content).group(0) + '\n\n\n'
            featureHeader_by_file[feature_file] = feature_head_with_tags

    logger.info('Splitting cases...')

    sequence_tag = sequence_tag.replace('@', '')
    for feature_file_path in feature_files_paths:
        source_feature, filename_head = feature_file_path

        with open(source_feature, 'r') as feature_file:
            feature_content = feature_file.read()

        # get tags above Feature name
        feature_tags = set(tag_regexp.findall(featureHeader_by_file[source_feature]))
        testcases_found = case_regexp.findall(feature_content, re.IGNORECASE)
        parallel_testcases = []

        # get parallel testcases and add to first file @serial cases
        sequence_tag_found = False
        feature_header_written = False
        for case in testcases_found:
            case_tags = set(tag_regexp.findall(case[0]))
            # matched tag in feature tags                    # matched tag in case tags
            if any((feature_tags.intersection(tags_list), case_tags.intersection(tags_list))):
                if '@' + sequence_tag in case[0]:
                    if not feature_header_written:
                        with open(filename_head + str(1) + '_' + sequence_tag + '.feature', 'a', encoding='utf-8') as result:
                            result.write(featureHeader_by_file[source_feature])
                        feature_header_written = True
                    sequence_tag_found = True

                    with open(filename_head + str(1) + '_' + sequence_tag + '.feature', 'a', encoding='utf-8') as result:
                        result.write(case[0] + '\n\n')

                else:
                    parallel_testcases.append(str(case[0] + '\n'))

        index = 1 if not sequence_tag_found else 2
        for case in parallel_testcases:
            with open(filename_head + str(index) + '.feature', 'a', encoding='utf-8') as result:
                result.write(featureHeader_by_file[source_feature])
                result.write(str(case) + '\n')
            index += 1

        logger.info(source_feature + '\tis splitted')

    logger.info('............SPLITTING COMPLETED............\n')


@main.command(short_help='split cases into n files. The number of files is set with the --files-number parameter')
@click.option('--features-dir', '-fd', "features_dir", default='./', type=str, show_default=True, help='source features directory')
@click.option('--files-number', '-num', "num_files", default=5, type=int, show_default=True, help='number of final files after splitting')
@click.option('--result-file-path', '-res', "result_dir", default='./', type=str, show_default=True, help='direcotry you want to save splitted files result')
@click.option('--sequence-tag', '-st', 'sequence_tag', type=str, default='@serial', show_default=True, help='tag to find and join dependent cases behind')
@click.option('--tags', '-t', 'tags', type=str, help='tags of needed cases [don`t works for behave tags expressions]')
def splitByGroups(features_dir, num_files, result_dir, sequence_tag, tags):
    
    Path(result_dir).mkdir(parents=True, exist_ok=True)

    features_list = [os.path.normpath(feature_path) for feature_path in glob(features_dir + '/*.feature')]
    tags_list = tags.replace(' ', '').split(',')

    feature_files_pathes = []
    result_files_with_counters = {}
    logger.info('Creating files...')
    for feature_file in features_list:
        # get all tags
        feature_content = open(feature_file, 'r').read()
        tags_in_feature = set(tag_regexp.findall(feature_content))
        if tags_in_feature.intersection(tags_list):
            # get filename part by format like 'par_<feature_name>_<num>
            filename_head = os.path.normpath(result_dir + '/' + "par_" + os.path.splitext(os.path.basename(feature_file))[0] + '_')
            tmp = [feature_file, filename_head]
            feature_files_pathes.append(tmp)
            # get feture head with tags ond Feature name
            feature_head_with_tags = feature_regexp.match(feature_content).group(0) + '\n\n\n'
            for i in range(num_files):
                result_filename = tmp[1] + str(i + 1) + '.feature'
                with open(result_filename, 'w+', encoding='utf-8') as touch:
                    touch.write(feature_head_with_tags)
                    logger.info(result_filename + '\tok')
                result_files_with_counters[result_filename] = 0

    logger.info('Splitting cases...')

    sequence_tag = sequence_tag.replace('@', '')

    for feature_file in feature_files_pathes:
        source_feature = feature_file[0]
        filename_head = feature_file[1]

        with open(source_feature, 'r') as feature:
            feature_content = feature.read()

        # get tags above Feature name
        feature_tags = set(tag_regexp.findall(
            feature_regexp.match(feature_content).group(0)
        ))
        testcases_found = case_regexp.findall(feature_content, re.IGNORECASE)
        parallel_testcases = []
        # get parallel testcases and add to first file @serial cases
        sequence_tag_found_flag = False
        for case in testcases_found:
            case_tags = set(tag_regexp.findall(case[0]))
            # matched tag in feature tags                    # matched tag in case tags
            if any(feature_tags.intersection(tags_list), case_tags.intersection(tags_list)):
                if '@' + sequence_tag in case[0]:
                    sequence_tag_found_flag = True
                    with open(filename_head + str(1) + '.feature', 'a', encoding='utf-8') as result:
                        result.write(case[0] + '\n\n')

                    result_files_with_counters[filename_head + str(1) + '.feature'] += 1
                else:
                    parallel_testcases.append(str(case[0] + '\n'))

        if sequence_tag_found_flag:
            counter = 1
            for case in parallel_testcases:
                for i in range(counter, num_files + 1):
                    if i != counter:
                        current_file_name = filename_head + str(i) + '.feature'
                        if result_files_with_counters[current_file_name] < result_files_with_counters[filename_head + str(1) + '.feature']:
                            with open(current_file_name, 'a', encoding='utf-8') as result:
                                result.write(str(case) + '\n')
                            
                            result_files_with_counters[current_file_name] += 1
                            counter = i
                            break
                        # if couters are equal
                        else:
                            with open(filename_head + str(1) + '.feature', 'a', encoding='utf-8') as result:
                                result.write(str(case) + '\n')

                            result_files_with_counters[filename_head + str(1) + '.feature'] += 1
                            counter = 1
                            break
                    # if end is reached and scenario is not added anywhere, write the scenario in file with smallest amount of cases
                    else:
                        if i == num_files and counter == num_files:
                            key_with_smallest_counter = min(
                                result_files_with_counters.keys(),
                                key=lambda x: result_files_with_counters[x] if filename_head in x else sys.maxsize  # don't ask about that
                            )
                            with open(key_with_smallest_counter, 'a', encoding='utf-8') as result:
                                result.write(str(case) + '\n')

                            result_files_with_counters[key_with_smallest_counter] += 1
                            counter = 1
                        continue
        else:
            for i, case in enumerate(parallel_testcases):
                with open(filename_head + str(i % num_files + 1) + '.feature', 'a', encoding='utf-8') as result:
                    result.write(str(case) + '\n')

        logger.info(source_feature + '\tis splitted')

    for filename in os.listdir(result_dir):
        file_path = os.path.join(result_dir, filename)
        if not case_regexp.search(open(file_path, 'r').read()):
            os.unlink(file_path)

    logger.info('............SPLITTING COMPLETED............\n')


@main.command(short_help='run already splitted cases (runs cases from files with "par_" prefix only)')
@click.option('--feature-dir', '-fd', 'feature_dir', type=str, default='./', show_default=True, help='feature root directory')
@click.option('--processes', '-p', type=int, default=5, show_default=True, help='number of processes')
@click.option('--no-skipped', '-k', is_flag=True, help='do not include skipped cases in report')
@click.option('--no-multithreaded-flag', is_flag=True, help='do not include option "-D run_mode="Multithreaded" to behave args')
@click.option('--no-capture', is_flag=True, help='do not include skipped cases in report')
@click.option('--tags', '-t', help='specify behave tags to run')
@click.option('--format', '-f', 'formatter', help='formatter')
@click.option('--venv', help='virtual environment')
@click.option('--outfile', '-o', help='outfile')
@click.option('--define', '-D', multiple=True, help='''Define user-specific data for the config.userdata dictionary.
                                                    Example: -D foo=bar to store it in config.userdata["foo"].''')
def run(feature_dir, processes, no_skipped, no_multithreaded_flag, no_capture, tags, formatter, venv, outfile, define):
    features = glob(feature_dir + '/par*.feature')
    features = [os.path.normpath(feature) for feature in features]

    params = ""
    if no_skipped: params += " --no-skipped "
    if no_capture: params += " --no-capture "
    if tags: params += f" --tags={tags} "
    if outfile: params += f" -o {outfile}"
    if formatter: params += f" -f {formatter} "
    if define: params += f" -D {' -D '.join(define)} "

    if not no_multithreaded_flag:
        params += ' -D behave_run_mode=Multithreaded '

    args = {
        "params": params,
        "venv": venv if venv else False
    }

    processes_time = {}

    run_feature = partial(_run_feature, args=args)

    logger.info(f"Found {len(features)} features")
    with Pool(processes) as pool:
        for pid, duration_time, feature, status in pool.map(run_feature, features):
            print(f"{feature}: {status}!!")
            if pid in processes_time.keys():
                processes_time[pid] += duration_time
            else:
                processes_time[pid] = duration_time

    # LOG THREAD TIMES
    times_table = PrettyTable(['PID', 'Time (s)'])
    for pid in processes_time.keys():
        times_table.add_row([pid, processes_time[pid]])

    with open("processes_time_log.log", "w") as time_log:
        time_log.write(times_table.get_string())
    
    logger.info("\n\nTime per process: \n" + times_table.get_string())


def _run_feature(feature, args):
    if args["venv"]:
        cmd = "{venv}/behave {params} {feature}".format(venv=args["venv"], params=args["params"], feature=feature)
    else:
        cmd = "behave {params} {feature}".format(params=args["params"], feature=feature)

    logger.info(cmd.replace('  ', ' '))
    
    logger.info("pool pid: " + str(os.getpid()))

    start_time = time.time()
    r = call(cmd, shell=True)
    duration_time = int(time.time() - start_time)

    status = 'ok' if r == 0 else 'failed'
    return str(os.getpid()), duration_time, feature, status


if __name__ == '__main__':
    main()
