"""
kvm_stat prints statistics generated by the kvm module.
It depends on debugfs. If no debugfs is mounted, the profiler
will try to mount it so it's possible to proceed.

@copyright: Red Hat 2010
@author: Lucas Meneghel Rodrigues (lmr@redhat.com)
"""
import os, subprocess, logging
from autotest.client import utils, profiler, os_dep
from autotest.client.shared import error


class kvm_stat(profiler.profiler):
    """
    kvm_stat based profiler. Consists on executing kvm_stat -l during a given
    test execution, redirecting its output to a file on the profile dir.
    """
    version = 1
    def initialize(self, **dargs):
        """
        Gets path of kvm_stat and verifies if debugfs needs to be mounted.
        """
        self.is_enabled = False

        kvm_stat_installed = False
        try:
            self.stat_path = os_dep.command('kvm_stat')
            kvm_stat_installed = True
        except ValueError:
            logging.error('Command kvm_stat not present')

        if kvm_stat_installed:
            try:
                utils.run("%s --batch" % self.stat_path)
                self.is_enabled = True
            except error.CmdError, e:
                if 'debugfs' in str(e):
                    try:
                        utils.run('mount -t debugfs debugfs /sys/kernel/debug')
                    except error.CmdError, e:
                        logging.error('Failed to mount debugfs:\n%s', str(e))
                else:
                    logging.error('Failed to execute kvm_stat:\n%s', str(e))


    def start(self, test):
        """
        Starts kvm_stat subprocess.

        @param test: Autotest test on which this profiler will operate on.
        """
        if self.is_enabled:
            cmd = "%s -l" % self.stat_path
            logfile = open(os.path.join(test.profdir, "kvm_stat"), 'w')
            p = subprocess.Popen(cmd, shell=True, stdout=logfile,
                                 stderr=subprocess.STDOUT)
            self.pid = p.pid
        else:
            logging.error('Asked for kvm_stat profiler, but kvm_stat not '
                          'present')


    def stop(self, test):
        """
        Stops profiler execution by sending a SIGTERM to kvm_stat process.

        @param test: Autotest test on which this profiler will operate on.
        """
        if self.is_enabled:
            try:
                os.kill(self.pid, 15)
            except OSError:
                pass


    def report(self, test):
        """
        Report function. Does nothing as there's no postprocesing needed.

        @param test: Autotest test on which this profiler will operate on.
        """
        return None