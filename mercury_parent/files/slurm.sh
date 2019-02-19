#!/bin/bash
#SBATCH --partition=normal
#SBATCH --ntasks=1
#SBATCH --output=<name>_%J_stdout.txt
#SBATCH --error=<name>_%J_stderr.txt
#SBATCH --time=<timelimit>
#SBATCH --job-name=<name>-%J
#SBATCH --workdir=<workdir>
#SBATCH --requeue

cd "<workdir>"; ./<cmd> ; cd "<workdir>"; touch ./finished

exit 0
