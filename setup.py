# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

LOGO='dxcommd_logo.png'
if os.name == 'nt':
    DXCOMM_DIR="c:\\dxcommd"
    ICONE="dxcomm.ico"
    INI1="nt/dxcomm.ini"
    INI2="nt/dxexec.ini"
    import py2exe
    
    setup(name="dxcommd",
          version="4.0",
          description="Comunicador dotX",
          author="João Alfredo Gama Batista",
          author_email="joaoalf@dotx.com.br",
          url="http://www.dotx.com.br",
          namespace_package=['dx'],
          package_dir={'': 'src'},
          packages=find_packages('src'),
          windows=[{"script":"dxcommd.py","icon_resources":[(1,ICONE)]},
		"dxexec.py"],
          data_files=[(DXCOMM_DIR, [ICONE, INI1]),
		(DXCOMM_DIR, [ICONE, INI2]),
		(DXCOMM_DIR, [ICONE, LOGO])]
          )
else:
    DXCOMM_DIR="/usr/local/dxcommd"
    ICONE="dxcomm.xpm"
    INI1="posix/dxcomm.ini"
    INI2="posix/dxexec.ini"
    setup(name="dxcommd",
          version="4.0",
          description="Comunicador de sistemas dotX",
          author="João Alfredo Gama Batista",
          author_email="joaoalf@dotx.com.br",
          url="http://www.dotx.com.br",
          scripts=["dxcommd", "dxexec"],
          namespace_package=['dx'],
          package_dir={'': 'src'},
          packages=find_packages('src'),
          #py_modules=['dxcomm.dxcommd', 'dxcomm.dxexec', 'dxcomm.gui'],
          data_files=[(DXCOMM_DIR, [ICONE, INI1]),
		(DXCOMM_DIR, [ICONE, INI2]),
		('/etc/init.d', ['scripts/dxcommd'])]
          )
