from setuptools import setup

with open('requirements.txt', 'r') as file:
    REQUIREMENTS = [x for x in file.read().splitlines() if x]

README = open('README.md', 'r').read()


setup(
    name='fattest-cat',
    version='0.1.0',
    author='Andrew Mussey',
    description='List the cats at the San Francisco SPCA by weight.',
    long_description=README,
    install_requires=REQUIREMENTS,
    py_modules=['fetch_cats'],
    entry_points={
        'console_scripts': [
            'fattest-cat = fetch_cats:main'
        ]
    }
)
