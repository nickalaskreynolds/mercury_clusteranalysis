"""Submit and manage mercury jobs."""

# internal modules
import os
from argparse import ArgumentParser as ap
import threading
import queue
import re
from time import sleep, time
import itertools

# external modules
from nkrpy.load import load_cfg, verify_dir
from nkrpy.files import freplace
from nkrpy.mp import run_seq_command as run_command
from nkrpy.coordinates import checkconv

# relative modules
import construct_jobs

# global attributes
__all__ = ('test', 'main')
__doc__ = """."""
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)
__version__ = 0.1

__max_queue__ = -1

"""
read config > timelimit jobname dir cmd num_sim
run job checker in bg (threading)
write slurm file > above
slurm file calls construct_jobs
slurm file cd and calls the mercury program
"""


def worker(q, f, wkr):
    """Worker wrapper for threading queue."""
    """Receives call to being queue, gets qeueue
    item val, submits job, checks for job status,
    adds to final array and quits."""
    while True:
        try:
            item = q.get(block=True, timeout=10)
            if item is None:
                break
            date = str(time()).replace('.', '-')
            print(f'Working on {item[0] + 1}')
            construct_jobs.main(item[1], date)
            build_slurm(item[1], date)
            item = sub_job(item[1], item[0] + 1, date)
            f.add(item)
            q.task_done()
        except queue.Empty:
            print(f'Worker {wkr} is exiting due to timeout.')
            break
        sleep(0.01)
    pass


def fill_queue(cfg, q):
    count = itertools.count()
    limit = checkconv(cfg.timelimit) * 3600.
    while True:
        n = count.__next__()
        try:
            q.put([n, cfg], block=True, timeout=limit)
        except queue.Full:
            print("Filler exiting, timeout/full")
            break
        if (n >= cfg.num_simulations) and (cfg.num_simulations != -1):
            print(f'Queue filled: {n}')
            break
        sleep(0.01)
    pass


def build_slurm(cfg, modelnum):
    dest = f'{cfg.destination}/{cfg.naming_schema}/' +\
        f'{cfg.naming_schema}_sim{modelnum}'.replace('//', '/')
    freplace(f'{dest}/slurm.sh', '<name>', cfg.naming_schema)
    freplace(f'{dest}/slurm.sh', '<timelimit>', cfg.timelimit)
    freplace(f'{dest}/slurm.sh', '<workdir>', dest)
    freplace(f'{dest}/slurm.sh', '<cmd>', cfg.program)
    with open(f'{cfg.destination}/{cfg.naming_schema}/' +
              f'slurm_master_restart_{cfg.time}.sh', 'a') as f:
        f.write(f'sbatch {dest}/slurm.sh &\n')
    with open(f'{cfg.destination}/{cfg.naming_schema}/' +
              f'refresh_outputs_{cfg.time}.sh', 'a') as f:
        f.write(f'cd {cfg.naming_schema}_sim{modelnum} ;' +
                f' ./element6 ;echo "Finished {modelnum}"\n')

def recover_job(string):
    """Parse jobnumber."""
    regex = '(\d+)'
    matches = re.finditer(regex, string, re.MULTILINE)
    try:
        match = matches.__next__()
    except:
        return False
    if match:
        return int(match.group())


def check_status(jobnum):
    """Check jobstatus."""
    uname = 'whoami'
    result = run_command([uname]).__next__().decode("utf-8").strip('\n')
    queue = "squeue -u <uname>".replace('<uname>', result)  # noqa
    for i, output in enumerate(run_command(queue.split(' '))):
        output = output.decode("utf-8").strip('\n')
        if str(jobnum) in output:
            return True
    print('Job finished:', jobnum)
    return False


def sub_job(cfg, jobnum, modelnum):
    dest = f'{cfg.destination}/{cfg.naming_schema}/' +\
           f'{cfg.naming_schema}_sim{modelnum}/'.replace('//', '/')
    job = False
    sub_count = 0
    while not job and ((sub_count / 60.) < checkconv(cfg.timelimit) *
                       3600. * 1.1):
        run = f'sbatch {dest}slurm.sh'
        result = run_command(run.split(' ')).__next__()\
            .decode("utf-8").strip('\n')
        job = recover_job(result)
        sub_count += 1
        sleep(1)
    if job:
        print(f'Submitted Job {jobnum} ID: {job}...in dir: <{dest}>')
        return job
    else:
        print('Timeout occured')


def job_manager(cfg):
    """Main job handler."""
    # startup workers
    __job_start__ = queue.Queue(maxsize=__max_queue__)
    __job_finish__ = set()
    cfg.sub = {}

    threads = [threading.Thread(target=worker, args=(__job_start__,
                                __job_finish__, i))
               for i in range(cfg.num_threads)]

    threads.insert(0, threading.Thread(target=fill_queue,
                                       args=(cfg, __job_start__)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f'Finished Submitting these jobs:\n{__job_finish__}')
    pass


def main(cfg_name):
    """Main caller function."""
    config = load_cfg(cfg_name)
    config.time = str(time()).replace('.', '_')
    dest = f'{config.destination}/{config.naming_schema}/'.replace('//', '/')
    verify_dir(dest, True)
    job_manager(config)
    exit()
    pass


def test():
    """Testing function for module."""
    pass


if __name__ == "__main__":
    """Directly Called."""
    parser = ap()
    parser.add_argument('-c', help='configuration file', default='config.py')
    args = parser.parse_args()

    print('Running Job')
    main(args.c)
    print('Finished')

# end of code
