from distutils.core import setup

setup(
    name='serialcommander',
    version='0.4.1',
    url='https://github.com/carlgonz/SerialCommander',
    license='GPL v3',
    author='Carlos Gonzalez',
    author_email='contacto.carlosgonzalezqgmail.com',
    description='A simple serial interface to send commands',

    packages=['forms'],
    py_modules=['serialcommander', "client"],
    scripts=['serialcommander.py', ],
    include_package_data=True,
    install_requires=["pyzmq", ],
    data_files=[('config', ['config/config.json']), ]
)
