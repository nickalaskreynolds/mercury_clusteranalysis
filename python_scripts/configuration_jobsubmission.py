"""Configuration file for the contruct_jobs."""
# flake8: noqa

# file modifiers
parent_mercury_inputs = '../mercury_parent/files/'  # noqa the template input file locations
parent_mercury_programs = '../mercury_parent/'  # the location for the programs
destination = '/home/reynolds/mercury_results'  # destination for results, will end up as dest/naming_schema_simN
naming_schema = 'multiprocessRestricted2body'  # naming schema as 'naming_schema_simN/'

# oscer params
num_threads = 10
num_simulations = 10  # number of simulations
timelimit = '00:15:00'  # timelimit for each run hh:mm:ss
program = 'mercury6_4mult_passstarsfeelplum_instantremove_closeenc_nogasdisk'  # noqa name of program to run

# integrator config
stop_time = 365.25e8  # days
output_time = 365.25E4  # days
timestep = 100E0  # days

# cluster
cluster_mass = 1.E-12  # mass of the cluster in msun
cluster_radius = 50000.0  # radius of the cluster in au
days_for_interaction = 365E7  # days for interactions to take place
plummer_model = True

# primary source
central_l_mass = 1.  # mass of central potential Msun
central_u_mass = 1.  # mass of central potential Msun

# handle binary object
binary_mass = 0.5
binary_density = 5.43
binary_l_sma = 5
binary_u_sma = 10
binary_l_ecc = 1E-15
binary_u_ecc = 1E-14
binary_l_inc = 0
binary_u_inc = 90

# handle bodies
num_bodies_l = 1  # max number of bodies within an orbit
num_bodies_u = 8  # max number of bodies within an orbit
bodies_l_mass = 0.001  # lower mass of bodies
bodies_u_mass = 0.1  # upper mass of bodies
bodies_l_density = 5.43  # lower density of bodies in Msun
bodies_u_density = 5.43  # upper density of bodies in Msun
avg_dist = 100  # average distance between bodies within orbit in AU
lower_smajora = 5  # Semi-major axis lower bound AU
upper_smajora = 8  # Semi Major axis upper bound AU
lower_ecc = 1E-15  # ecc lower bound
upper_ecc = 1E-14  # ecc upper bound
lower_inc = 0  # inc lower bound
upper_inc = 90  # inc upper bound

# end of config
