from setuptools import setup

setup(
    name="sp_cli",
    version='0.1',
    py_modules=['sp_cli'],
    install_requires=[
        'Click',
        'silverpeak',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        sp_cli=sp_cli:main
    ''',
)