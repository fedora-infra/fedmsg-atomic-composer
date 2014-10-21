from setuptools import setup

setup(
    name='fedmsg_atomic_composer',
    version='0.0.1',
    license='GPLv3',
    description='Composes Atomic rpm-ostrees when Fedora repositories are updated',
    author='Luke Macken',
    author_email='lmacken@redhat.com',
    url='',
    install_requires=['fedmsg', 'mock'],
    packages=[],
    entry_points="""
    [moksha.consumer]
    fedmsg_atomic_composer = fedmsg_atomic_composer:AtomicComposer
    """,
)
