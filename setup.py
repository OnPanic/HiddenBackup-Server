from distutils.core import setup

setup(
    # Application name:
    name="hiddenbackupd",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Juan Ezquerro LLanes",
    author_email="arrase@gmail.com",

    # Packages
    packages=["HiddenBackup"],

    # Details
    url="https://github.com/OnPanic/HiddenBackup-Server",

    description="Hidden backup service over Tor",

    data_files=[
        ('/etc/init.d', ['etc/init.d/hiddenbackupd']),
        ('/etc/', ['etc/hiddenbackupd.conf']),
        ('/usr/sbin', ['hiddenbackupd'])
    ],
    requires=['stem']
)
