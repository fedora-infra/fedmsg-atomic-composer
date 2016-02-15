from setuptools import setup

setup(
    name='fedmsg-atomic-composer',
    version='2016.2',
    license='GPLv3',
    description='Composes Atomic rpm-ostrees when Fedora repositories are updated',
    author='Luke Macken',
    author_email='lmacken@redhat.com',
    url='https://github.com/fedora-infra/fedmsg-atomic-composer',
    install_requires=['fedmsg', 'mako'],
    tests_require=['mock'],
    packages=['fedmsg_atomic_composer'],
    package_data={'fedmsg_atomic_composer': ['templates/*.mako']},
    entry_points="""
    [moksha.consumer]
    fedmsg_atomic_composer = fedmsg_atomic_composer.consumer:AtomicConsumer
    [console_scripts]
    fedmsg-atomic-composer-cli = fedmsg_atomic_composer.cli:cli
    """,
)
