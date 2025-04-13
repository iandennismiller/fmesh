# fmesh

from setuptools import setup, find_packages

setup(
    version='0.1.0',
    name='fmesh',
    description="fmesh",
    packages=find_packages(),
    scripts=[
        "scripts/fmesh-tui",
    ],
    include_package_data=True,
    keywords='',
    author="thecookingsenpai, svofski, iandennismiller",
    author_email="",
    install_requires=[
        "pubsub",
        "meshtastic",
        "python-dotenv",
        "textual",
    ],
    license='MIT',
    zip_safe=False,
)
