"""."""

# internal modules

# external modules
from nkrpy.mercury.file_loader import parse_aei

# relative modules

# global attributes
__all__ = ('test', 'main')
__doc__ = """."""
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)
__version__ = 0.1



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




def main():
    """Main caller function."""
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
