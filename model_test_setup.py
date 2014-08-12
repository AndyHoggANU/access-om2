
from __future__ import print_function

import subprocess as sp
import shlex
import re
import os
import glob
import time

class ModelTestSetup(object):

    def __init__(self): 

        self.my_path = os.path.dirname(os.path.realpath(__file__))
        self.lab_path = os.path.join(self.my_path, 'lab')
        self.bin_path = os.path.join(self.lab_path, 'bin')

    def wait(self, run_id):
        """
        Wait for the qsub job to terminate. 
        """

        while True:
            time.sleep(5)
            qsub_out = ''
            try:
                qsub_out = sp.check_output(['qstat', run_id], stderr=sp.STDOUT)
            except sp.CalledProcessError as err:
                qsub_out = err.output

            if 'Job has finished' in qsub_out:
                break


    def run(self, expt_path, lab_path):
        """
        Run the given experiment using payu and check output.

        """

        os.chdir(expt_path)
        cmd = 'payu sweep --laboratory {}'.format(lab_path)
        sp.check_output(shlex.split(cmd))
        cmd = 'payu run -n 1 --laboratory {}'.format(lab_path)
        run_id = sp.check_output(shlex.split(cmd))
        run_id = run_id.strip()

        self.wait(run_id)
        run_id = run_id.split('.')[0]

        # Read qsub output file and return to caller.
        stdout_filename = glob.glob('*.o{}'.format(run_id))
        assert(len(stdout_filename) == 1)
        stdout = ''
        with open(stdout_filename[0], 'r') as f:
            stdout = f.read()

        stderr_filename = glob.glob('*.e{}'.format(run_id))
        assert(len(stderr_filename) <= 1)
        stderr = ''
        if len(stderr_filename) == 1:
            with open(stderr_filename[0], 'r') as f:
                stderr = f.read()

        # Read the qsub id of the collate job from the output. 
        m = re.search(r'\n(\d{7}.r-man2)\n', stdout)
        assert(m is not None)
        # Wait for the collate to complete. 
        self.wait(m.group(1))

        # Files created by qsub.
        files = [os.path.abspath(f) for f in glob.glob('*.o[0-9]*')]

        os.chdir(self.my_path)

        return stdout, stderr, files

