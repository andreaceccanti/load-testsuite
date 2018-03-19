from common import *
from srm import *
from jarray import array
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback
import time
import random
import uuid

error           = grinder.logger.error
info            = grinder.logger.info
debug           = grinder.logger.debug

props           = grinder.properties

utils           = Utils(grinder.properties)

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY  = props['rm_test.directory']
TEST_NUMFILES   = int(props['rm_test.number_of_files'])

def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def setup_thread_dir():

    info("Setting up rm test.")
    endpoint, client = utils.get_srm_client()

    dir_name = str(uuid.uuid4())
    base_dir = get_base_dir()
    test_dir = "%s/%s" % (base_dir, dir_name)
    
    info("Creating remote test directory ... " + base_dir)
    srmMkDir(client, get_surl(endpoint, base_dir))
    
    info("Creating rm-test specific test dir: " + test_dir)
    test_dir_surl = get_surl(endpoint, test_dir)
    check_success(srmMkDir(client, test_dir_surl))
    
    info("rm setup completed successfully.")
    
    return test_dir

def setup_run(thread_dir):
    
    info("Setting up rm test run.")
    endpoint, client = utils.get_srm_client()
    
    dir_name = str(uuid.uuid4())
    run_test_dir = "%s/run_%s" % (thread_dir, str(grinder.getRunNumber()))
    
    info("Creating rm-test run-specific test dir: " + run_test_dir)
    run_test_dir_surl = get_surl(endpoint, run_test_dir)
    check_success(srmMkDir(client, run_test_dir_surl))
    
    surls = []
    for i in range(1, TEST_NUMFILES + 1):
        surl = get_surl(endpoint, "%s/file_%s" % (run_test_dir, i))
        surls.append(surl)
        debug("appended: %s" % surl)
    
    info("Creating rm-test test dir files ... ")
    token, response = srmPtP(client,surls,[])
    check_success(response)
    check_success(srmPd(client,surls,token))

    info("rm run setup completed successfully.")
    return surls

def rm_files(surls):
    
    endpoint, client = utils.get_srm_client()
    response = srmRm(client, surls)
    info("Rm %s - [%s %s]" % (surls, response.returnStatus.statusCode, response.returnStatus.explanation))
    log_result_file_status(response)
    check_success(response)

def cleanup(test_dir):
    
    info("Cleaning up for rm-test.")
    endpoint, client = utils.get_srm_client()
    response = client.srmRmdir(get_surl(endpoint, test_dir), 1)
    print_srm_op("rmdir", response)
    check_success(response)
    info("rm-test cleanup completed successfully.")


class TestRunner:

    def __init__(self):
        self.thread_dir = setup_thread_dir()

    def __call__(self):
        try:
            test = Test(TestID.RM_TEST, "StoRM srmRm files")
            test.record(rm_files)

            surls = setup_run(self.thread_dir)
            rm_files(surls)

        except Exception, e:
            error("Error executing rm-files: %s" % traceback.format_exc())
    
    def __del__(self):
        
        cleanup(self.thread_dir)