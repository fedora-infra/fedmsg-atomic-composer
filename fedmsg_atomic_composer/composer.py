# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import copy
import json
import time
import shutil
import logging
import tempfile
import subprocess
import pkg_resources

from datetime import datetime
from mako.template import Template

from .config import config


class AtomicComposer(object):
    """An atomic ostree composer"""

    def compose(self, release):
        release = copy.deepcopy(release)
        release['tmp_dir'] = tempfile.mkdtemp()
        release['timestamp'] = time.strftime('%y%m%d.%H%M')
        try:
            self.setup_logger(release)
            self.update_configs(release)
            self.update_repos(release)
            self.generate_mock_config(release)
            self.init_mock(release)
            self.ostree_init(release)
            self.generate_repo_files(release)
            self.ostree_compose(release)
            self.update_ostree_summary(release)
            self.cleanup(release)
            release['result'] = 'success'
        except:
            self.log.exception('Compose failed')
            release['result'] = 'failed'
            self.log.error(release)
        return release

    def setup_logger(self, release):
        name = '{name}-{timestamp}'.format(**release)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        log_dir = release['log_dir']
        log_file = os.path.join(log_dir, name)
        release['log_file'] = log_file
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        stdout = logging.StreamHandler()
        handler = logging.FileHandler(log_file)
        log_format = ('%(asctime)s -  %(levelname)s - %(filename)s:'
                      '%(module)s:%(lineno)d - %(message)s')
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        stdout.setFormatter(formatter)
        stdout.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.addHandler(stdout)
        self.log = logger

    def cleanup(self, release):
        """Cleanup any temporary files after the compose"""
        shutil.rmtree(release['tmp_dir'])

    def update_configs(self, release):
        """ Update the fedora-atomic.git repositories for a given release """
        git_repo = release['git_repo']
        git_dir = release['git_dir'] = os.path.join(release['tmp_dir'],
                                                    os.path.basename(git_repo))
        self.call(['git', 'clone', '-b', release['git_branch'],
                   git_repo, git_dir])

    def update_repos(self, release):
        for repo, url in config['repos'].items():
            if repo not in release['repos']:
                release['repos'][repo] = url.format(**release)

    def mock_cmd(self, release, cmd):
        """Run a mock command in the chroot for a given release"""
        cmd = isinstance(cmd, list) and cmd or [cmd]
        self.call(['/usr/bin/mock', '--new-chroot', '-r', release['mock'],
                   '--configdir=' + release['mock_dir']] + cmd)

    def init_mock(self, release):
        """Initialize/update our mock chroot"""
        root = '/var/lib/mock/%s' % release['mock']
        if not os.path.isdir(root):
            self.mock_cmd(release, '--init')
            self.log.info('mock chroot initialized')
        else:
            self.mock_cmd(release, '--update')
            self.log.info('mock chroot updated')

    def generate_mock_config(self, release):
        """Dynamically generate our mock configuration"""
        mock_tmpl = pkg_resources.resource_string(__name__, 'templates/mock.mako')
        mock_dir = release['mock_dir'] = os.path.join(release['tmp_dir'], 'mock')
        mock_cfg = os.path.join(release['mock_dir'], release['mock'] + '.cfg')
        os.mkdir(mock_dir)
        for cfg in ('site-defaults.cfg', 'logging.ini'):
            os.symlink('/etc/mock/%s' % cfg, os.path.join(mock_dir, cfg))
        with file(mock_cfg, 'w') as cfg:
            cfg.write(Template(mock_tmpl).render(**release))

    def mock_shell(self, release, cmd):
        self.mock_cmd(release, ['--shell', cmd])

    def generate_repo_files(self, release):
        """Dynamically generate our yum repo configuration"""
        repo_tmpl = pkg_resources.resource_string(__name__, 'templates/repo.mako')
        repo_file = os.path.join(release['git_dir'], '%s.repo' % release['repo'])
        with file(repo_file, 'w') as repo:
            repo.write(Template(repo_tmpl).render(**release))
        self.log.info('Wrote repo configuration to %s', repo_file)

    def ostree_init(self, release):
        out = release['output_dir']
        base = os.path.dirname(out)
        if not os.path.isdir(base):
            self.log.info('Creating %s', base)
            os.makedirs(base, mode=0755)
        if not os.path.isdir(out):
            cmd = 'ostree --repo=%s init --mode=archive-z2'
            self.mock_shell(release, cmd % out)

    def ostree_compose(self, release):
        start = datetime.utcnow()
        cmd = 'rpm-ostree compose tree --repo=%s %s'
        treefile = os.path.join(release['git_dir'], 'treefile.json')
        with file(treefile, 'w') as tree:
            json.dump(release['treefile'], tree)
        self.mock_shell(release, cmd % (release['output_dir'], treefile))
        self.log.info('rpm-ostree compose complete (%s)',
                      datetime.utcnow() - start)

    def update_ostree_summary(self, release):
        """Update the ostree summary file and return a path to it"""
        self.log.info('Updating the ostree summary for %s', release['name'])
        cmd = 'ostree --repo=%s summary --update' % release['output_dir']
        self.mock_shell(release, cmd)
        return os.path.join(release['output_dir'], 'summary')

    def call(self, cmd, **kwargs):
        """A simple subprocess wrapper"""
        self.log.info('Running %s', cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)
        out, err = p.communicate()
        if out:
            self.log.info(out)
        if err:
            self.log.error(err)
        if p.returncode != 0:
            self.log.error('returncode = %d' % p.returncode)
            raise Exception
        return out, err, p.returncode
