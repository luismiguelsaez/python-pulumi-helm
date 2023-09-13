import os
import re

from distutils.core import setup

ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')

requires = [
  'pulumi-kubernetes>=4.1.1,<5.0.0',
  'pulumi>=3.82.0,<4.0.0',
],

def get_version():
    init = open(os.path.join(ROOT, 'python_pulumi_helm', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)
  
setup(name='python-pulumi-helm',
      version=get_version(),
      description='Python Pulumi Helm charts',
      url='https://github.com/luismiguelsaez/python-pulumi-helm',
      install_requires=requires
)
