from setuptools import setup

setup(
    name='fedmsg-atomic-composer',
    version='0.0.1',
    license='GPLv3',
    description='Composes Atomic rpm-ostrees when Fedora repositories are updated',
    author='Luke Macken',
    author_email='lmacken@redhat.com',
    url='https://github.com/lmacken/fedmsg-atomic-composer',
    install_requires=['fedmsg', 'mock'],
    packages=['fedmsg_atomic_composer'],
    entry_points="""
    [moksha.consumer]
    fedmsg_atomic_composer = fedmsg_atomic_composer:AtomicComposer
    """,
)
