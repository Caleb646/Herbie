from setuptools import setup

setup(
    name='Herbie',
    version='0.1.0',    
    description='This Python library is designed to help you build and control a self-driving RC car using a Raspberry Pi.',
    url='https://github.com/Caleb646/Herbie/',
    author='Caleb Thomas',
    author_email='calebthomas646@yahoo.com',
    license='MIT',
    packages=[
        "Herbie",
        "Herbie.CarNav",
        "Herbie.Hardware",
        "Herbie.Network",
        "Herbie.CMath"
        ],
    install_requires=[
        "numpy>=1.2.1",
        "opencv-python"                     
        ],
    extras_require={
        "PiCamera": ["picamera[array]"], # Allow additional installs on pip install. For example pip install Herbie[PiCamera]
        "TFLite": ["tflite-support>=0.4.2", "protobuf>=3.18.0"] # pip install Herbie[TFLite] or both pip install Herbie[TFLite,PiCamera]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Operating System :: MacOS",       
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ]
)