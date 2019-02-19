"""This code finds the jacobi constant from given files."""

# standard
import os
from sys import version, float_info
# external
import matplotlib.pyplot as plt
import numpy as np
import math
from decimal import Decimal

print('Max Float Precision', float_info.max)

__version__ = float(version[0:3])
__cpath__ = '/'.join(os.path.realpath(__file__).split('/')[:-1])
_filetypes = ('.aei',)

__cwd__ = os.getcwd()


def load_cfg(fname):
    """Load configuration file as module."""
    if '/' not in fname:
        fname = __cwd__ + '/' + fname
    try:
        if __version__ >= 3.5:
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", fname)
            cf = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cf)
        elif __version__ >= 3.3:
            from importlib.machinery import SourceFileLoader
            cf = SourceFileLoader("config", fname).load_module()
        elif __version__ <= 3.0:
            import imp
            cf = imp.load_source('config', fname)
    except:
        print('Failed. Cannot find file <{}> or the fallback <config.py>'
              .format(fname))
        print('Or invalid line found in file. Try using import <{}> yourself'
              .format(fname[:-3]))
        exit(1)
    return cf


def load_variables(mod):
    """Given a module, load attributes directly to global."""
    if __name__ != "__main__":
        print('This will load/overwrite in new variables into global!')
    for k in dir(mod):
        if '__' not in k:
            globals()[k] = getattr(mod, k)


def _list_array(ite, dtype=np.float64):
    """Transform list to numpy array of dtype."""
    try:
        _shape = tuple([len(ite), len(ite[0])][::-1])
        _return = np.zeros(_shape, dtype=dtype)
        for i, x in enumerate(ite):
            for j, y in enumerate(x):
                _return[j, i] = y
    except TypeError as te:
        print('Not a 2D array...')
        _shape = len(ite)
        _return = np.zeros(_shape, dtype=dtype)
        for i, x in enumerate(ite):
            _return[i] = x
    print('Converted to shape with:',_return.shape)
    return _return


def _resolve_header(ite):
    _return = []
    for i, x in enumerate(ite):
        if ('(' in x) and (')' in x):
            _return[-1] = _return[-1] + x
        else:
            _return.append(x)
    return _return


def read_file(fname, _try=0):
    """Read various Mercury filetypes."""
    if not os.path.isfile(fname):
        print('File not found: ', fname)
        exit()

    _max = 10
    try:
        if '.aei' in fname:
            """Some logic for aei."""
            _header = 4 - _try - 1
            _to_start = 5 - _try
            header, data = None, []
            with open(fname, 'r') as f:
                for i, line in enumerate(f):
                    _tmp = [x for x in line.strip('\n').strip(' ')
                                           .split(' ') if x != '']
                    if i == (_header):
                        header = _tmp
                    elif i > _header:
                        data.append(_tmp)

        else:
            print('Filetype not recognized. Currently supported: {}'
                  .format(','.join(_filetypes)))
            exit()
    except UnicodeDecodeError as ue:
        print(ue, ' while reading file... cutting file to resolve')
        if _try == 0:
            os.system(f'sed -i.bak "1d" {fname}')
        else:
            os.system(f'sed -i "1d" {fname}')
        if _try >= _max:
            print('Failed', _max, ' times. Restoring file and exitting')
            os.system(f'mv -f {fname}.bak {fname}')
            exit()
        return None, None
    except ValueError as ve:
        print(ve, ' while reading file...')
        print(f'try:{_try}\nHeader:{header}')
        os.system(f'mv -f {fname}.bak {fname}')
        exit()
    else:
        if os.path.isfile(f'{fname}.bak'):
            os.system(f'mv -f {fname}.bak {fname}')
        return _resolve_header(header), _list_array(data)


def cross(a, b):
    """Compute cross product between a, b."""
    assert len(a) == len(b)
    if len(a) == 3:
        c = (a[1] * b[2] - a[2] * b[1],
             a[2] * b[0] - a[0] * b[2],
             a[0] * b[1] - a[1] * b[0])
    elif len(a) == 2:
        c = (0, 0, a[0] * b[1] - a[1] * b[0])
    return c


def dot(a, b):
    """Compute dot product between a and b."""
    ret = 0
    for i in range(len(a)):
        ret += a[i] * b[i]
    return ret


def mag(a):
    """Mag of a vector."""
    ret = 0
    for x in a:
        ret += x ** 2
    return (ret) ** 0.5


def find_jacobi(ob3, ob2):
    """Given values, return jacobi constant."""
    # https://farside.ph.utexas.edu/teaching/336k/Newtonhtml/node121.html
    t, x, y, z, vx, vy, vz, mass3 = ob3
    pe = -1. * mass3 / mag((x, y, z))
    ke = 0.5 * mass3 * mag((vx, vy, vz)) ** 2
    energy = pe + ke
    angular_momentum = (x * vx, y * vy, z * vz)
    t, x, y, z, vx, vy, vz, m2 = ob2
    angular_velocity = cross((x, y, z),(vx, vy, vz)) / mag((x, y, z)) ** 2
    # c = 2*(E-w*h)
    #print(cross((x, y, z),(vx, vy, vz)))
    #print(energy,angular_momentum,angular_velocity)
    return 2. * (energy - dot(angular_momentum,angular_velocity))


def main(fname):
    """Main caller for the program."""
    """Input filename for configuration file."""
    mod = load_cfg(fname)
    load_variables(mod)

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    _try = 0
    header, testdata = read_file(test_particle, _try)
    while (not header) and (not testdata):
        _try += 1
        print('On try', _try + 1)
        header, testdata = read_file(test_particle, _try)
    _try = 0
    header, bigdata = read_file(m2, _try)
    while (not header) and (not bigdata):
        _try += 1
        print('On try', _try + 1)
        header, bigdata = read_file(m2, _try)
    _try = 0
    header, smalldata = read_file(m3, _try)
    while (not header) and (not smalldata):
        _try += 1
        print('On try', _try + 1)
        header, smalldata = read_file(m3, _try)

    print('Header:', header)
    print('Data:', testdata.shape)

    E = []
    for i in range(testdata.shape[-1]):
        # print('Row',i)
        small_vals = smalldata[:, i]
        big_vals = bigdata[:, i]
        E.append(find_jacobi(small_vals, big_vals))

    E = _list_array(E)
    E = E[~np.isnan(E)]
    print(E)
    t = [x for x in range(E.shape[0])]

    print('Jacobi:', E.shape)

    plt.figure(figsize=(10, 10))
    if True:
        plt.plot(t, E / np.mean(E) - 1., 'b.', label='normed std: {0:.4}%'.format(np.std(E)/np.mean(E) * 100.))
    else:
        plt.loglog(t, E/ np.mean(E), 'b.', label='normed std: {0:.4}%'.format(np.std(E)/np.mean(E) * 100.))
    plt.xlabel('Time (Integration Units)')
    plt.ylabel('Normalized Jacobi Constant')
    plt.title('Jacobi Constant')
    plt.legend()
    plt.savefig(output_dir + '/jacobi.pdf')
    np.savetxt(output_dir + '/jacobi.npy', E)
    #plt.show()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='This programs finds the' +
                                     ' Jacobi constant given the appropriate' +
                                     ' files.')

    parser.add_argument('-i', '--input', dest='input', type=str, help='Input' +
                        ' config file')

    args = parser.parse_args()

    main(args.input)

# end of file
