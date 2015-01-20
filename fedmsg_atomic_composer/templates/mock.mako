config_opts['root'] = '${mock}'
config_opts['target_arch'] = '${arch}'
config_opts['dist'] = '${git_branch}'  # only useful for --resultdir variable subst
config_opts['releasever'] = '${version}'
config_opts['chroot_setup_cmd'] = 'install yum rpm-ostree'
config_opts['extra_chroot_dirs'] = ['/run/lock']
config_opts['plugin_conf']['bind_mount_enable'] = True
config_opts['plugin_conf']['bind_mount_opts']['dirs'].append(('${work_dir}', '${work_dir}'))
config_opts['plugin_conf']['bind_mount_opts']['dirs'].append(('${tmp_dir}', '${tmp_dir}'))
% for path in mount_dirs:
config_opts['plugin_conf']['bind_mount_opts']['dirs'].append(('${path}', '${path}'))
%endfor

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

% for repo_name, url in repos.items():

## Skip repos that aren't enabled in the treefile
% if repo_name not in treefile['repos']:
<% continue %>
% endif

[${repo_name}]
name=Fedora ${version} ${repo_name}
% if 'metalink' in url:
metalink=${url}
% else:
baseurl=${url}
% endif
enabled=1
cost=5000
% endfor
"""
config_opts['yum_common_opts'] = []
