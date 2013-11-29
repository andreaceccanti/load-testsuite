from java.util import Properties
from java.io import FileInputStream, BufferedInputStream
from net.grinder.script.Grinder import grinder
from org.slf4j import Logger, LoggerFactory
import os

PROPERTIES = "common.properties"

def get_logger(name):
    return LoggerFactory.getLogger(name)

def log_surl_call_result(op_name, res, logger=None):

    if logger is None:
        logger = grinder.logger.debug

    logger("%s result: %s (expl: %s)" %
           (op_name, res.returnStatus.statusCode,
            res.returnStatus.explanation))
    statuses = res.getArrayOfFileStatuses().getStatusArray()

    logger("surl(s) statuses:")
    for s in statuses:
        surl_attr_names = ["sourceSURL", "SURL", "surl"]
        fn = [ x for x in surl_attr_names if x in dir(s) ]
        if len(fn) == 0:
            raise Exception("SURL access methods %s not found in %s: %s" % (s,surl_attr_names,dir(s)))
        surl = getattr(s, fn[0])
        logger("%s -> %s" %(surl,
                            s.getStatus().getStatusCode()))

def load_common_properties():
    """Loads common test properties into grinder properties."""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(current_dir, PROPERTIES)
    source = BufferedInputStream(FileInputStream(file_name))
    props = Properties()
    props.load(source)
    source.close()

    for key in props.keySet().iterator():
        grinder.properties[key] = props.get(key)

class TestID():
    PTG       = 1
    SPTG      = 2
    PTP       = 3
    SPTP      = 4
    LS        = 5
    RM        = 6
    MKDIR     = 7
    RMDIR     = 8
    MV        = 9
    REL_FILES = 10
    TXFER_IN  = 11
    TXFER_OUT = 12
    PD        = 13

    PTG_SYNC  = 100
    PTP_SYNC  = 101