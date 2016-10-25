import cProfile, io, pstats

#
#   Logging
#
#   logfile - The path to a log file to write to.
#
#       A path string. "-" means log to stdout.
#
#   loglevel - The granularity of log output
#
#       A string of "debug", "info", "warning", "error", "critical"
#

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

    ## get traceback info
    import threading, sys, traceback
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""),
            threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename,
                lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    worker.log.debug("\n".join(code))

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")


def pre_request(worker, req):
    worker.log.warning("Got an request")
    #worker.log.info('enabling profiling')
    #worker.profile = cProfile.Profile()
    #worker.log.info('AAAAAAA type = {}'.format(worker.profile))
    #worker.profile.enable()
    # f = open('/usr/local/virtumedix/output.log', 'w+')
    #f.write(s.getvalue())
    # f.write('this is a teset')
    # f.close()
    #pass

def post_request(worker, req, *args):
    worker.log.warning("Finish request")
    #worker.log.info('disenabling profiling')
    #worker.profile.disable()
    #s = io.StringIO()
    #sortby = 'cumulative'
    #ps = pstats.Stats(worker.profile, stream=s).sort_stats(sortby)
    #ps.print_stats()
    #f = open('/usr/local/virtumedix/output.log', 'w+')
    #f.write(s.getvalue())
    #f.write('this is a teset')
    #f.close()
