# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

LOGO='dxcommd_logo.png'
if os.name == 'nt':
    DXCOMM_DIR="c:\\dxcommd"
    ICONE="dxcomm.ico"
    INI1="nt/dxcomm.ini"
    INI2="nt/dxexec.ini"
    try:
        import py2exe
    except ImportError:
        print "py2exe não encontrado!"
        sys.exit(-1)
    
    setup(name="dx.comm",
          version="4.0",
          description="Comunicador dotX",
          author="João Alfredo Gama Batista",
          author_email="joaoalf@dotx.com.br",
          url="http://www.dotx.com.br",
          namespace_package=['dx'],
          package_dir={'': 'src'},
          packages=find_packages('src'),
          windows=[{"script":"dxcommd.py","icon_resources":[(1,ICONE)]}, "dxexec.py"],
          data_files=[(DXCOMM_DIR, [ICONE, INI1]),
              (DXCOMM_DIR, [ICONE, INI2]),
              (DXCOMM_DIR, [ICONE, LOGO])],
          dependency_links=['https://github.com/joaoalf/dx.utils/tarball/master#egg=dx.utils-1.0'],
          install_requires=['dx.utils', 'wxPython']
          )
else:
    DXCOMM_DIR="/usr/local/dxcommd"
    ICONE="dxcomm.xpm"
    INI1="posix/dxcomm.ini"
    INI2="posix/dxexec.ini"
    setup(name="dx.comm",
          version="4.0",
          description="Comunicador de sistemas dotX",
          author="João Alfredo Gama Batista",
          author_email="joaoalf@dotx.com.br",
          url="http://www.dotx.com.br",
          #scripts=["dxcommd", "dxexec"],
          namespace_package=['dx'],
          package_dir={'': 'src'},
          packages=find_packages('src'),
          entry_points={'console_scripts':[
              'dxcommd = dx.comm.scripts:dxcommd',
              'dxexec = dx.comm.scripts:dxexec'],},
          #py_modules=['dxcomm.dxcommd', 'dxcomm.dxexec', 'dxcomm.gui'],
          data_files=[(DXCOMM_DIR, [ICONE, INI1]),
              (DXCOMM_DIR, [ICONE, INI2]),
              ('/etc/init.d', ['scripts/dxcommd'])],
          dependency_links=['https://github.com/joaoalf/dx.utils/tarball/master#egg=dx.utils-1.0'],
          install_requires=['dx.utils',]
          )

