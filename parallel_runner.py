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
import os
import sys


logging.basicConfig(level=logging.INFO, format="[%(levelname)-8s %(asctime)s] %(message)s")
logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def main(context):
    '''
    The program was created in order to provide parallel execution of cases, despite the fact that behave does not support this.
    Standard work algorithm:\n
    1) split cases by files using the "split" command \n
    2) run the cases using the "run" command \n\n

    _____  \n
    Authors:\n
        Danil Manmarev \n
        Dmitriy Sherstianikh \n
        Dmitriy Basov \n
        Kirill Nikolaev \n

    ( ͡° ͜ʖ ͡°)
    '''
    pass


@main.command(short_help='split cases to files with one case only (cases with a sequential tag will be in the first file)')
@click.option('--features-dir', '-fd', "features_dir", default='./', type=str, show_default=True, help='source features directory')
@click.option('--result-file-path', '-res', "result_dir", default='./', type=str, show_default=True, help='direcotry you want to save splitted files result')
@click.option('--sequence-tag', '-st', 'sequence_tag', type=str, default='@serial', show_default=True, help='tag to find and join dependent cases behind')
@click.option('--tags', '-t', 'tags', type=str, help='tags of needed cases [don`t works for behave tags expressions]')
def split(features_dir, result_dir, sequence_tag, tags):

    Path(result_dir).mkdir(parents=True, exist_ok=True)
    # if there are old .feature files in 'parallel' directory, purge them
    for f in os.listdir(result_dir):
        os.remove(os.path.join(result_dir, f))

    required_tags = tags.replace(' ', '').split(',')
    if not sequence_tag.startswith('@'):
        sequence_tag = '@' + sequence_tag

    logger.info('Splitting normal cases...')

    index = 1
    serial_index = 0
    seq_tag_mapping = {}
    sequence_cases = {}

    feature_files_paths = []
    feature_files = [os.path.normpath(feature_path) for feature_path in glob(features_dir + '/*.feature')]

    for feature_file in feature_files:

        # check the file. if it has none of the tags we need, skip it
        with open(feature_file, 'r') as f:
            feature_content = f.read().strip()
        if not any(tag in feature_content for tag in required_tags):
            continue

        # get filename part by format like 'par_<feature_name>_<num>
        filename_head = f"{result_dir}/par_{os.path.splitext(os.path.basename(feature_file))[0]}_"
        # blocks header - case1 - case2 - ... are split by '\n\n' in standard feature file format
        feature_blocks = feature_content.split('\n\n')

        feature_header = feature_blocks[0] + '\n\n\n'
        # tags are in the first line of a header / case
        feature_tags = set(feature_header.split('\n')[0].strip().split())
        # exclude cases that are commented out
        all_cases = [case.strip() for case in feature_blocks[1:]]
        feature_cases = ['    ' + case for case in all_cases if not case.startswith('#')]

        # get parallel testcases and store @serial testcases for later
        for case in feature_cases:
            case_tags = set(case.split('\n')[0].strip().split())

            # matched tag in feature tags                    # matched tag in case tags
            if any((feature_tags.intersection(required_tags), case_tags.intersection(required_tags))):
                if sequence_tag in case:
                    # join @serial files by tag intersection (CASES FROM DIFFERENT SERIES MUST NOT INTERSECT)
                    num_tags = sorted([tag for tag in case_tags if all(ch.isnumeric() for ch in tag[1:])])
                    is_different_sequence = True
                    for tag in num_tags:
                        if tag in seq_tag_mapping:
                            is_different_sequence = False
                            break
                    serial_index += is_different_sequence
                    seq_tag_mapping.update(zip(num_tags, [serial_index] * len(num_tags)))
                    idx_to_assign = seq_tag_mapping[num_tags[0]]

                    try:
                        sequence_cases[idx_to_assign]['cases'].append(case)
                    except KeyError:
                        sequence_cases[idx_to_assign] = {'header': feature_header, 'cases': [case]}
                else:
                    with open(f"{filename_head}{index}.feature", 'w', encoding='utf-8') as result:
                        result.write(feature_header)
                        result.write(case + '\n')
                    index += 1
        logger.info(feature_file + '\tis splitted')

        logger.info('Splitting sequence cases...')

        for case_info in sequence_cases.values():
            with open(f"{filename_head}sequence_{index}.feature", 'w', encoding='utf-8') as result:
                result.write(case_info['header'])
                result.write('\n\n'.join(case_info['cases']))
            index += 1

    logger.info('............SPLITTING COMPLETED............\n')


@main.command(short_help='run already splitted cases (runs cases from files with "par_" prefix only)')
@click.option('--feature-dir', '-fd', 'feature_dir', type=str, default='./', show_default=True, help='feature root directory')
@click.option('--processes', '-p', type=int, default=5, show_default=True, help='number of processes')
@click.option('--no-skipped', '-k', is_flag=True, help='do not include skipped cases in report')  # same help?
@click.option('--enable-multithread', is_flag=True, help='include option "-D run_mode="Multithreaded" to behave args')
@click.option('--no-capture', is_flag=True, help='do not include skipped cases in report')  # same help?
@click.option('--tags', '-t', help='specify behave tags to run')
@click.option('--format', '-f', 'formatter', help='formatter')
@click.option('--venv', help='virtual environment')
@click.option('--outfile', '-o', help='outfile')
@click.option('--define', '-D', multiple=True, help='''Define user-specific data for the config.userdata dictionary.
                                                    Example: -D foo=bar to store it in config.userdata["foo"].''')
def run(feature_dir, processes, no_skipped, enable_multithread, no_capture, tags, formatter, venv, outfile, define):
    features = glob(feature_dir + '/par*.feature')
    features = [os.path.normpath(feature) for feature in features]

    params = []
    if no_skipped:
        params.append("--no-skipped")
    if no_capture:
        params.append("--no-capture")
    if tags:
        params.append(f"--tags={tags}")
    if outfile:
        params.append(f"-o {outfile}")
    if formatter:
        params.append(f"-f {formatter}")
    if define:
        params.append(f"-D {' -D '.join(define)}")
    if enable_multithread:
        params.append("-D behave_run_mode=Multithreaded")

    args = {
        "params": ' '.join(params),
        "venv": venv or False
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
    cmd = f"behave {args['params']} {feature}"

    if args["venv"]:
        cmd = f"{args['venv']}/{cmd}"

    logger.info(cmd.replace('  ', ' '))

    logger.info("pool pid: " + str(os.getpid()))

    start_time = time.time()
    r = call(cmd, shell=True)
    duration_time = int(time.time() - start_time)

    status = 'ok' if r == 0 else 'failed'
    return str(os.getpid()), duration_time, feature, status


if __name__ == '__main__':
    main()
