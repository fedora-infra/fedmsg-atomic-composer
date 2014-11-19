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

import click

from fedmsg_atomic_composer.composer import AtomicComposer
from fedmsg_atomic_composer.config import config


@click.command()
@click.argument('release')
def compose(release):
    releases = config['releases']
    if release not in releases:
        click.echo('Unknown release. Valid releases are: %s' % releases.keys())
        return

    release = releases[release]
    composer = AtomicComposer()
    result = composer.compose(release)
    if result['result'] == 'success':
        click.echo('{name} tree successfuly composed'.format(**result))
    else:
        click.echo('{name} tree compose failed'.format(**result))

    click.echo('Log: {log_file}'.format(**result))


if __name__ == '__main__':
    compose()
