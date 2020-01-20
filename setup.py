from setuptools import find_packages, setup

requirements = []

with open('requirements.txt', 'r') as f:
    for resource in f.readlines():
        if not resource.startswith('git+'):
            requirements.append(resource.strip())

setup(
    name='prozorro_auction',
    version_format='{tag}',
    setup_requires=['setuptools-git-version'],
    description='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements + ["prozorro_crawler==1.0.8"],
)
