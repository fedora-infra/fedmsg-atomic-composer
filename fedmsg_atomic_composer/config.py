config = dict(
    releases={
        # {'name': 'rawhide', 'repo': 'rawhide', 'version': 'development',
        # 'tree': 'docker-host'},
        # {'name': 'f21-gold', 'repo': 'gold', 'version': '21', 'arch':
        # 'x86_64', 'tree': 'docker-host', 'mock': 'fedora-21-x86_64'},
        'f21-updates': {
            'name': 'f21-updates',
            'repo': 'updates',
            'version': '21',
            'arch': 'x86_64',
            'tree': 'docker-host',
            'treefile': {
                'include': 'fedora-atomic-docker-host.json',
                'ref': 'fedora-atomic/f21/x86_64/updates/docker-host',
                'repos': ['fedora-21', 'updates'],
            },
            'mock': 'fedora-21-updates-x86_64',
            'git_branch': 'f21',

            # Add additional, or overwrite yum repository urls.o
            # This is so tools like bodhi can point to their own
            # local mashes when composing trees.
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
                'selinux': False,
            },
            'git_branch': 'f21',
            'mock': 'fedora-21-updates-testing-x86_64',
            'repos': {},
        },
    },

    repos={
        'updates': 'https://dl.fedoraproject.org/pub/fedora/linux/updates/{version}/{arch}/',
        'updates-testing': 'https://dl.fedoraproject.org/pub/fedora/linux/updates/testing/{version}/{arch}/',
    },

    output_dir='/srv/fedora-atomic/{version}/{arch}/{repo}/{tree}',
    log_dir='/srv/fedora-atomic/logs/{version}/{arch}/{repo}/{tree}',
    git_repo='https://git.fedorahosted.org/git/fedora-atomic.git',
    verbose=True,

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
    map_to_release=('output_dir', 'log_dir', 'git_repo'),
)

for key in config.get('map_to_release', []):
    for name, release in config['releases'].items():
        release[key] = config[key].format(**release)
