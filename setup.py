from distutils.core import setup

setup(
    name="Ecomb",
    version="0.1.0",
    description="Python personal-commodity price tracking engine.",
    author="Darren James Wight",
    author_email="d.j.wight@gmail.com",
    packages=["Efind"],
    install_requires=["pandas>=1.3.5"],
)
