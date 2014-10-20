from setuptools import setup

setup(
    name='ostreecomposer',
    version='0.0.1',
    license='GPLv3',
    description='Composes OSTrees when Fedora repositories are updated',
    author='Luke Macken',
    author_email='lmacken@redhat.com',
    url='',
    install_requires=['fedmsg', 'mock'],
    packages=[],
    entry_points="""
    [moksha.consumer]
    ostreecomposer = ostreecomposer:OSTreeComposer
    """,
)
