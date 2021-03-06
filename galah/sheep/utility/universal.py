import signal, sys, logging, threading, platform

# Will be set to True when the program is exiting.
exiting = False

# Thrown as an exception when a thread needs to exit
class Exiting:
    pass

# The Queue of containers that the producer will add to and the consumers will
# pull from.
containers = None

# When a consumer loses its shepherd after it has processed a test request, it
# will kill itself and put the results into this queue.
orphaned_results = None

# The application-wide ZMQ context used to create sockets
context = None

# The command line options the user passes in
cmdOptions = None

# The system information sent to the Shepherd so it knows what kind of test
# requests we can safely process
environment = {
    "system": platform.system(),
    "release": platform.release(),
    "machine": platform.machine(),
    "tools": [
        {"name": "python", "version": platform.python_version()}
    ]
}

class ShepherdLost(Exception):
    def __init__(self, current_request = None, result = None):
        self.current_request = current_request
        self.result = result

        Exception.__init__(self)

# Create a decorator to allow thread's run functions to handle exiting
# exceptions.
_log = logging.getLogger("galah.sheep.universal")
def handleExiting(zfunc):
    def newFunc(*zargs, **zkwargs):
        try:
            zfunc(*zargs, **zkwargs)
        except Exiting:
            pass
        except ShepherdLost:
            _log.warning(
                "%s's thread aborted with a ShepherdLost exception.",
                threading.currentThread().name
            )
        except Exception:
            _log.exception(
                "%s's thread aborted with an exception.",
                threading.currentThread().name
            )

        _log.info("%s's thread exited" % threading.currentThread().name)
    return newFunc
