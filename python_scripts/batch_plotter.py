"""Batch plotting sequence."""

# internal modules
import threading
import queue
from glob import glob
import re

# external modules
from nkrpy.load import load_cfg
from nkrpy.mercury.file_loader import parse_aei
from nkrpy.miscmath import cross, dot, mag
from nkrpy.mp import run_seq_command as run_command
import matplotlib.pyplot as plt
import numpy as np

# relative modules

# global attributes
__all__ = ('test', 'main')
__doc__ = """."""
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)
__version__ = 0.1

__max_queue__ = -1


def find_jacobi(ob3, ob2):
    """Given values, return jacobi constant."""
    # https://farside.ph.utexas.edu/teaching/336k/Newtonhtml/node121.html
    t, x, y, z, vx, vy, vz, mass3 = ob3
    pe = -1. * mass3 / mag((x, y, z))
    ke = 0.5 * mass3 * mag((vx, vy, vz)) ** 2
    energy = pe + ke
    angular_momentum = (x * vx, y * vy, z * vz)
    t, x, y, z, vx, vy, vz, m2 = ob2
    angular_velocity = cross((x, y, z), (vx, vy, vz)) / mag((x, y, z)) ** 2
    # c = 2*(E-w*h)
    # print(cross((x, y, z),(vx, vy, vz)))
    # print(energy,angular_momentum,angular_velocity)
    return 2. * (energy - dot(angular_momentum, angular_velocity))


def get_data(file):
    ret = parse_aei(file)
    return ret[0], ret[-1]


def get_sim_num(cfg, files):
    ret = tuple(set([f.split('/')[-2].strip(cfg.naming_schema)
                     for f in files]))
    return ret


def gather_files(directory: str):
    all_aei_files = glob(f'{directory}/*.aei')
    all_params = glob(f'{directory}/*/param.in')
    all_big = glob(f'{directory}/*/big.in')
    if len(all_files) == 0:
        print('No aei files found.')
        exit(1)
    return all_aei_files, all_params, all_big


def main(cfgname_plotter, cfgname_job):
    """Main caller function."""
    """
    load all files
    masterbinaries.shape # sims * 9 * timestep (sim number, mass, density, x y z vx vy v)
    masterbody.shape # body files * sim # * 10 * timestep (sim number, body num, mass, density, x y z vx vy vz)
    cluster_Files.shape #sim * 4 (cluster mass * cluster radius central potential initial coords of testp)
    plot e vs radius from central potential (color bodies and )
    plot
    """
    cfg_p = load_cfg(cfgname_plotter)
    cfg_j = load_cfg(cfgname_job)
    cfg_p.all_aei_files, cfg_p.all_params, cfg_p.all_big = \
        gather_files(cfg_p.file_location)
    cfg_p.sims = get_sim_num(cfg_j, cfg_p.all_params)

    pass


def job_manager(cfg_plotter, cfg_jon):
    """Main job handler."""
    # startup workers
    __job_start__ = queue.Queue(maxsize=__max_queue__)
    __job_finish__ = set()

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
        if (n >= cfg.):
            print(f'Queue filled: {n}')
            break
        sleep(0.01)
    pass



def test():
    """Testing function for module."""
    pass


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    test()
    print('Test Passed')

# end of code
