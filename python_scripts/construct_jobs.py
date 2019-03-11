"""Contruct the mercury jobs for submission."""

# internal modules
import os
from argparse import ArgumentParser as ap
import shutil
from glob import glob
from decimal import Decimal
import subprocess
from importlib import reload
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

# external modules
import numpy as np
from nkrpy.keplerian import orbital_params
from nkrpy.load import load_cfg, verify_dir, mod_2_dict
from nkrpy.files import freplace
from nkrpy.miscmath import plummer_radius, sample
from nkrpy.functions import format_decimal
from nkrpy.constants import msun, g, au, kepler

# relative modules

# global attributes
__all__ = ('test', 'main')
__doc__ = """."""
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)
__version__ = 0.1
_cwd_ = __path__
if _cwd_ == '':
    _cwd_ = os.getcwd()


def generate_sim(cfg, orbitals, jobnumber):
    """Generate the simulations wrapper."""
    # generate a tmp directory
    dest = f'{cfg.destination}/{cfg.naming_schema}/'.replace('//', '/')
    os.makedirs(dest, exist_ok=True)
    verify_dir(dest)
    os.chdir(dest)

    # bodies for a single sim
    sim_name = f'{dest}{cfg.naming_schema}_sim{jobnumber}'
    # copy over program files
    try:
        shutil.copytree(f'{_cwd_}/{cfg.parent_mercury_inputs}',
                        f'{sim_name}', symlinks=True)
    except shutil.Error:
        print(f'Jobnumber: <{jobnumber}> must be purely unique within directory <{dest}> and isn\'t.') # noqa
        exit()
    except Exception as e:
        print(f'Error: {e}')
        pass

    for x in glob(f'{_cwd_}/{cfg.parent_mercury_programs}/*'):
        dname = x.split("/")[-1]
        if not os.path.isfile(f'{dest}/{dname}') and os.path.isfile(x):
            print(f'Creating program: {x} in \n{dest}/{dname}')
            shutil.copyfile(x, f'{dest}/{dname}')
            shutil.copystat(x, f'{dest}/{dname}')
    print('Made files')
    if not os.path.isfile(f'{dest}/{cfg.program}'):
        print(f'Could not find the compiled mercury file: <{dest}/{cfg.program}>\nPlease go into the <{dest}> and run the makefile.')
        exit()

    # handle the 'big.in' file
    # generating binary
    central_mass = cfg.sub[f'{jobnumber}']['central_mass']
    binary_params = orbital_params(cfg.binary_l_sma,
                                   cfg.binary_u_sma,
                                   cfg.binary_l_ecc,
                                   cfg.binary_u_ecc,
                                   cfg.binary_l_inc,
                                   cfg.binary_u_inc,
                                   central_mass, size=1)[1][0]
    binary_params = [x for x in list(map(lambda x: format_decimal(x, 4),
                                         list(binary_params)))]

    inp_repl = ''
    # insert logic for binary
    binary_mass = cfg.sub[f'{jobnumber}']['binary_mass']
    inp_repl += f' WB m={binary_mass}D0 r=0.D0 d={cfg.binary_density}D0\n'
    inp_repl += f'  {" ".join(binary_params[0:3])}\n'
    inp_repl += f'  {" ".join(binary_params[3:])}\n'
    inp_repl += f'  0.D0 0.D0 0.D0\n'

    # now handle bodies
    cfg.sub[f'{jobnumber}']['mass_bodies'] = sample(cfg.bodies_l_mass,
        cfg.bodies_u_mass, size=cfg.sub[f'{jobnumber}']['num_bodies']) # noqa
    cfg.sub[f'{jobnumber}']['den_bodies'] = sample(cfg.bodies_l_density,
        cfg.bodies_u_density, size=cfg.sub[f'{jobnumber}']['num_bodies']) # noqa
    from IPython import embed
    for b, body in enumerate(orbitals):
        inp_repl += f" BODY{b}    m={cfg.sub[f'{jobnumber}']['mass_bodies'][b]}D0 r=0.D0 d={cfg.sub[f'{jobnumber}']['den_bodies'][b]}D0\n" # noqa
        tmp = [x for x in list(map(lambda x: format_decimal(x, 4),
                                   list(body)))]
        inp_repl += f'  {" ".join(tmp[0:3])}\n'
        inp_repl += f'  {" ".join(tmp[3:])}\n'
        inp_repl += f'  0.D0 0.D0 0.D0\n'
    # insert login for testp
    if cfg.plummer_model:
        plum_mass_enc = np.random.rand(1)[0]
        plum_radius = plummer_radius(plum_mass_enc, cfg.cluster_radius)
        cfg.plum_mass_enc = plum_mass_enc
        cfg.plum_radius = plum_radius
        random_xyz = False
        # choose
        while not isinstance(random_xyz, np.ndarray):
            points = np.abs(np.array(sample(0, 1, size=3)))
            norm = np.sqrt(np.sum(points ** 2))
            if norm == 0:
                random_xyz = False
            else:
                points *= plum_radius
                random_xyz = points
        # now get the velocity
        vel = np.sqrt(cfg.cluster_mass * msun * g / (plum_radius * au)) / au
        random_vel = False
        while not isinstance(random_vel, np.ndarray):
            points = np.array([np.random.choice([-1,1]) * x
                               for x in np.array(sample(0, 1, size=3))])
            norm = np.sqrt(np.sum(points ** 2))
            if norm == 0:
                random_vel = False
            else:
                points *= vel
                random_vel = points
        testp = np.concatenate([random_xyz, random_vel])
        testp = [x for x in list(map(lambda x: format_decimal(x, 4),
                                     list(testp)))]
    else:
        testp = ['0.D0' for x in range(6)]
    inp_repl += f'TESTP m=1.D-81 r=0.D0 d=0.D0\n'
    inp_repl += f'  {" ".join(testp[0:3])}\n'
    inp_repl += f'  {" ".join(testp[3:])}\n'
    inp_repl += f'  0.D0 0.D0 0.D0\n'

    freplace(f'{sim_name}/big.in', '<input>', inp_repl)

    # handle cluster.in file
    freplace(f'{sim_name}/cluster.in', '<mass>', '{}'.format(cfg.cluster_mass, '.15f'))
    freplace(f'{sim_name}/cluster.in', '<radius>', '{}'.format(cfg.cluster_radius, '.2f'))
    freplace(f'{sim_name}/cluster.in', '<days_for_interaction>', '{}'.format(int(cfg.days_for_interaction)))

    # handle param.in
    def compute_timestep(mass, state_vec):
        orb = xyz_2_orbital(state_vec[np.newaxis, :], mass)[0]
        print(orb, mass)
        return ((1. / (kepler * mass)) * (orb[0] ** 3)) ** 0.5 / 20.

    timestep = compute_timestep(central_mass, orbitals[0, :])
    freplace(f'{sim_name}/param.in', '<stop>', '{}'.format(cfg.stop_time))
    freplace(f'{sim_name}/param.in', '<interval>', '{}'.format(cfg.output_time))
    freplace(f'{sim_name}/param.in', '<timestep>', '{}'.format(int(np.ceil(timestep))))
    freplace(f'{sim_name}/param.in', '<mass>', '{}'.format(float(cfg.sub[f'{jobnumber}']['central_mass'])))
    freplace(f'{sim_name}/param.in', '<bb>', '{}'.format(int(cfg.sub[f'{jobnumber}']['num_bodies'])))

    # save config
    write_cfg = mod_2_dict(cfg)
    write_cfg['sub'] = write_cfg['sub'][f'{jobnumber}']
    write_cfg['sub']['job_number'] = f'{jobnumber}'
    with open(f'{sim_name}/configuration_params.pickle', 'wb') as f:
        pickle.dump(write_cfg, f, pickle.HIGHEST_PROTOCOL)
    pass


def main(config_name, jobnumber):
    """Main caller function."""
    # load cfg
    if isinstance(config_name, str):
        config = load_cfg(config_name)
    else:
        config = config_name
    try:
        config.sub[f'{jobnumber}'] = {}
    except:
        config.sub = {}
        config.sub[f'{jobnumber}'] = {}
    config.sub[f'{jobnumber}']['central_mass'] = sample(config.central_l_mass, config.central_u_mass, size=1)[0]
    nb_u, nb_l, avgdist, lsma, usma, lecc, uecc, linc, uinc = \
        config.num_bodies_u, config.num_bodies_l, config.avg_dist, \
        config.lower_smajora, config.upper_smajora, \
        config.lower_ecc, config.upper_ecc, \
        config.lower_inc, config.upper_inc
    config.sub[f'{jobnumber}']['binary_mass'] = sample(config.binary_l_mass, config.binary_u_mass, size=1, resample=True, lim=config.sub[f'{jobnumber}']['central_mass'], logic='<')[0]
    mass = config.sub[f'{jobnumber}']['central_mass']
    # generate lower orbit runs
    orbits = []
    nbod = np.int(np.abs(sample(nb_l, nb_u, size=1)))
    config.sub[f'{jobnumber}']['num_bodies'] = nbod
    for n in range(nbod):
        orbits.append(
            orbital_params(lsma + n * avgdist, usma +
                    n * avgdist, lecc, uecc, # noqa
                    linc, uinc, mass, # noqa
                    size=1)[1][0]) # noqa
    config.sub[f'{jobnumber}']['orbitals'] = orbits
    generate_sim(config, orbits, jobnumber)
    pass

if __name__ == "__main__":
    """Directly Called."""
    parser = ap()
    parser.add_argument('-c', help='configuration file', default='config.py')
    parser.add_argument('-j', help='jobnumber', type=int, default=0)
    args = parser.parse_args()

    print('Constructing')
    main(args.c, args.j)
    print('Finished')

# end of code
