## A mako template for yum repo files.
## These are written along-side of the treefile.json,
## which are then picked up by rpm-ostree.
% for repo, url in repos.items():

## Skip repos that aren't enabled in the treefile
% if repo not in treefile['repos']:
<% continue %>
% endif

[${repo}]
name=Fedora ${version} ${repo}
% if 'metalink' in url:
metalink=${url}
% else:
baseurl=${url}
% endif
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-${version}-${arch}
enabled=0
metadata_expire=0
skip_if_unavailable=False
%endfor
