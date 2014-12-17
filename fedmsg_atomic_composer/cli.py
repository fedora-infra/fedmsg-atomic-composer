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
import time
import tempfile
import pprint

from fedmsg_atomic_composer.composer import AtomicComposer
from fedmsg_atomic_composer.config import config

def get_release(release):
    releases = config['releases']
    if release not in releases:
        raise click.BadParameter('Unknown release. Valid releases are: %s' %
                                 releases.keys())
    return releases[release]


@click.group()
def cli():
    pass


@cli.command(help='Compose an ostree for a given release')
@click.argument('release')
def compose(release):
    release = get_release(release)
    composer = AtomicComposer()
    result = composer.compose(release)
    if result['result'] == 'success':
        click.echo('{name} tree successfuly composed'.format(**result))
    else:
        click.echo('{name} tree compose failed'.format(**result))
        click.echo(str(result))

    click.echo('Log: {log_file}'.format(**result))


@cli.command(help='List available releases')
@click.option('--json', is_flag=True)
def releases(json):
    if json:
        click.echo(pprint.pformat(config['releases']))
    else:
        for release in config['releases']:
            click.echo(release)


@cli.command()
@click.argument('release')
def clean(release):
    release = get_release(release)
    composer = AtomicComposer()
    release['tmp_dir'] = tempfile.mkdtemp()
    release['timestamp'] = time.strftime('%y%m%d.%H%M')
    composer.setup_logger(release)
    composer.generate_mock_config(release)
    composer.mock_cmd(release, '--clean')


if __name__ == '__main__':
    cli()
