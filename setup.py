from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="AWS Snapshot Automator",
    version="0.0.1",
    author="Mervin Hemaraju",
    author_email="mervin.hemaraju@checkout.com",
    description="A tool to facicilitate snapshots on AWS",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/mervin-hemaraju-cko/aws-snapshot-script",
    packages=find_packages()
)