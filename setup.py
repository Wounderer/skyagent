from setuptools import setup

setup(name='skyagent',
      version='0.1',
      description='Skywifi agent',
      url='https://github.com/Wounderer/skyagent.git',
      author='SkyWifi',
      author_email='kk@skywifi.pro',
      license='MIT',
      packages=['skyagent'],
      scripts=['bin/skyagent'],
      install_requires=[
          'twisted',
          'txaio',
          'autobahn'
      ],
      zip_safe=False)
