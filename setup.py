from distutils.core import setup

setup(
    name="Ecomb",
    version="0.1.0",
    description="Python personal Haus or Wohnung search and alert engine.",
    author="Darren James Wight",
    author_email="d.j.wight@gmail.com",
    packages=["HausFinder"],
    install_requires=[
        "pandas>=1.3.5",
        "requests-html>=0.10.0",
        "selenium>=4.1.0",
        "pyOpenSSL>=21.0.0",
        "pytest>=7.1.2",
    ],
)
