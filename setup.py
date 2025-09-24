import setuptools
setuptools.setup(
    name='LCAutomate',
    version='1.0',
    scripts=['./scripts/LCAutomate'],
    author='James Bamber, Logisymetrix Inc',
    description='This runs automated LCA',
    packages=setuptools.find_packages(),
    install_requires=[
        'setuptools',
        'pandas',
        'openpyxl',
        'networkx',
        'requests',
    ],
    python_requires='>=3.12'
)