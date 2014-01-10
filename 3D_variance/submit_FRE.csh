#!/bin/csh

# Requested queue
#$ -q himem.q

# Name of job
#$ -N frealign

# Use openmpi parallel environment; set number of slots
#$ -pe orte 1

# Max walltime for this job is X minutes
#$ -l h_rt=144:00:00

# Merge the standard out and standard error to one file
##$ -j y

# Run job through csh shell
#$ -S /bin/csh

# Use current working directory
#$ -cwd

# Change to current working directory
cd $SGE_O_WORKDIR

# The following is for reporting only. It is not needed
# to run the job. It will show up in your output file.
echo "Job starting `date`"
echo "Current working directory: $cwd"
echo "Got $NSLOTS slots."

set ref=$1

# The job

/home/michael/TFIID_IIA_DNA/Cryo/11may10a/FREAL_3Dvar/REF1/mult_reconstruct.com 1 12921 5 $ref

