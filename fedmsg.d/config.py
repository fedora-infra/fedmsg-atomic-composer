config = dict(
    fedmsg_atomic_composer=True,
    topic = ['org.fedoraproject.prod.bodhi.updates.fedora.sync',
             'org.fedoraproject.prod.compose.branched.rsync.complete',
             'org.fedoraproject.prod.compose.rawhide.rsync.complete',
             'org.fedoraproject.stg.bodhi.updates.fedora.sync',
             'org.fedoraproject.stg.compose.branched.rsync.complete',
             'org.fedoraproject.stg.compose.rawhide.rsync.complete',
             'org.fedoraproject.dev.bodhi.updates.fedora.sync',
             'org.fedoraproject.dev.compose.branched.rsync.complete',
             'org.fedoraproject.dev.compose.rawhide.rsync.complete'],
    touch_dir='/srv/inbox/',
    watch_dir='/srv/fedora-atomic/output',
)
