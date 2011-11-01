__author__ = 'joaoalf'

def dxcommd():
    import sys, os
    from dx.comm.dxcommd import Main

    INI_FILE='/usr/local/dxcommd/dxcomm.ini'

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    os.chdir('/')
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    app = Main(INI_FILE)
    app.go()

def dxexec():
    from dx.comm import dxexec

    dxexec.Main()

    