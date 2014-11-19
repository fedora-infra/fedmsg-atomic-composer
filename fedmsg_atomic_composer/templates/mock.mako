config_opts['root'] = '${mock}'
config_opts['target_arch'] = '${arch}'
config_opts['chroot_setup_cmd'] = 'install yum rpm-ostree'
config_opts['dist'] = '${git_branch}'  # only useful for --resultdir variable subst
config_opts['plugin_conf']['root_cache_enable'] = False
config_opts['internal_dev_setup'] = False
config_opts['plugin_conf']['bind_mount_opts']['dirs'].append(('/srv/fedora-atomic', '/srv/fedora-atomic'))
config_opts['plugin_conf']['bind_mount_opts']['dirs'].append(('/dev', '/dev'))
config_opts['plugin_conf']['bind_mount_opts']['dirs'].append(('${tmp_dir}', '${tmp_dir}'))

config_opts['yum.conf'] = """
[main]
cachedir=/var/cache/yum
debuglevel=2
reposdir=/dev/null
logfile=/var/log/yum.log
retries=20
obsoletes=1
gpgcheck=0
assumeyes=1
metadata_expire=0

[fedora]
name=fedora
baseurl=http://kojipkgs.fedoraproject.org/mash/branched/${arch}/os
enabled=1
cost=5000

% for repo_name, url in repos.items():
% if repo_name == 'updates-testing':
    % if repo != repo_name:
        <% continue %>
    % endif
% endif
[${repo_name}]
name=Fedora ${version} ${repo_name}
baseurl=${url}
enabled=1
cost=5000
% endfor
"""
config_opts['yum_common_opts'] = []
