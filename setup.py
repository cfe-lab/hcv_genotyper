import setuptools

import hcv_genotyper


install_requires = ["biopython >=1.72, < 4.0"]

setuptools.setup(
    name="hcv_genotyper",
    version=hcv_genotyper.__version__,
    packages=setuptools.find_packages(),
    author="Nathaniel Knight",
    author_email="nknight@cfenet.ubc.ca",
    description="Determine the genotype of HCV sequences using BLAST",
    license="Apache2",
    url="https://github.com/hcv-shared/hcv_genotyper",
    python_requires=">=3.5",
    install_requires=install_requires,
    test_suite="tests",
)
