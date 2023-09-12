from distutils.core import setup

setup(name='python-pulumi-helm',
      version='0.1.2',
      description='Python Pulumi Helm charts',
      url='https://github.com/luismiguelsaez/python-pulumi-helm',
      install_requires=[
        'pulumi-kubernetes>=4.1.1,<5.0.0',
        'pulumi>=3.82.0,<4.0.0',
      ],
)
