from setuptools import setup

setup(
    name='ostreecomposer',
    version='0.0.1',
    description='',
    author='',
    author_email='',
    url='',
    install_requires=["fedmsg"],
    packages=[],
    entry_points="""
    [moksha.consumer]
    ostreecomposer = ostreecomposer:OSTreeComposer
    """,
)
