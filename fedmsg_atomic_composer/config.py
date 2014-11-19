config = dict(
    releases={
        'f21-updates': {
            'name': 'f21-updates',
            'repo': 'updates',
            'version': '21',
            'arch': 'x86_64',

            # OSTree treefile configuration
            # https://github.com/projectatomic/rpm-ostree/blob/master/doc/treefile.md
            'tree': 'docker-host',
            'treefile': {
                'include': 'fedora-atomic-docker-host.json',
                'ref': 'fedora-atomic/f21/x86_64/updates/docker-host',
                'repos': ['fedora-21', 'updates'],
            },

            # The name of the mock container to build and maintain
            'mock': 'fedora-21-updates-x86_64',

            # The git branch to use in the `git_repo` for the parent
            # treefile & repo configurations
            'git_branch': 'f21',

            # Add or overwrite yum repository name:urls. This lets you
            # compose trees against your own repositories.
            'repos': {},
        },

        'f21-updates-testing': {
            'name': 'f21-updates-testing',
            'repo': 'updates-testing',
            'version': '21',
            'arch': 'x86_64',
            'tree': 'docker-host',
            'treefile': {
                'include': 'fedora-atomic-docker-host.json',
                'ref': 'fedora-atomic/f21/x86_64/updates-testing/docker-host',
                'repos': ['fedora-21', 'updates', 'updates-testing'],
            },
            'git_branch': 'f21',
            'mock': 'fedora-21-updates-testing-x86_64',
            'repos': {},
        },
    },

    # Package repositories to use in the mock container and ostree compose
    repos={
        'updates': 'https://dl.fedoraproject.org/pub/fedora/linux/updates/{version}/{arch}/',
        'updates-testing': 'https://dl.fedoraproject.org/pub/fedora/linux/updates/testing/{version}/{arch}/',
    },

    # Output directories
    output_dir='/srv/fedora-atomic/{version}/{arch}/{repo}/{tree}',
    log_dir='/srv/fedora-atomic/logs/{version}/{arch}/{repo}/{tree}',

    # The git repo containing our parent treefiles and yum repos
    git_repo='https://git.fedorahosted.org/git/fedora-atomic.git',

    # Mock command
    mock_cmd='/usr/bin/mock --new-chroot -r {mock}',

    # OSTree commands
    ostree_init='/usr/bin/ostree --repo={output_dir} init --mode=archive-z2',
    ostree_compose='/usr/bin/rpm-ostree compose tree --workdir-tmpfs --repo={output_dir} %s',
    ostree_summary='/usr/bin/ostree --repo={output_dir} summary --update',

    # fedmsg-specific configuration
    fedmsg_atomic_composer=True,
    config_key='fedmsg_atomic_composer',
    topic=['org.fedoraproject.prod.bodhi.updates.fedora.sync',
           'org.fedoraproject.prod.compose.branched.rsync.complete',
           'org.fedoraproject.prod.compose.rawhide.rsync.complete',
           'org.fedoraproject.stg.bodhi.updates.fedora.sync',
           'org.fedoraproject.stg.compose.branched.rsync.complete',
           'org.fedoraproject.stg.compose.rawhide.rsync.complete',
           'org.fedoraproject.dev.bodhi.updates.fedora.sync',
           'org.fedoraproject.dev.compose.branched.rsync.complete',
           'org.fedoraproject.dev.compose.rawhide.rsync.complete'
    ],

    # Map and expand certain global variables to each release
    map_to_release=('output_dir', 'log_dir', 'git_repo', 'mock_cmd',
                    'ostree_init', 'ostree_compose', 'ostree_summary'),
)

for key in config.get('map_to_release', []):
    for name, release in config['releases'].items():
        release[key] = config[key].format(**release)
