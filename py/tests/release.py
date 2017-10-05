import os
import getopt
import sys
import tempfile
import time
import unittest
import argparse
import urllib3
import shutil

import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis.external_api import ExternalApi
from swagger_client.api_client import ApiClient

def executable(temp_dir):
    return os.path.join(temp_dir, "bin", "epoch")

def extract_tarball(tarball_name, temp_dir):
    print("Extracting tar to " + temp_dir)
    os.system("tar xC " + temp_dir + " -f " + tarball_name)

def stop_node(temp_dir):
    print("Stopping")
    os.system(executable(temp_dir) + " stop")

def start_node(temp_dir):
    binary = executable(temp_dir) 
    assert os.path.isfile(binary)
    assert os.access(binary, os.X_OK)
    print("Starting " + binary)
    os.system(binary + " start")

def read_argv(argv):
    parser = argparse.ArgumentParser(description='Integration test a potential release')
    parser.add_argument('--maxheight', type=int, default=10,
                        help='Number of blocks to mine')
    parser.add_argument('--tarball', required=True, 
                        help='Release package tarball')

    args = parser.parse_args()
    tar_file_name = args.tarball
    max_height = args.maxheight
    return (tar_file_name, max_height)

def tail_logs(temp_dir, log_name):
    n = 200 # last 200 lines
    f = os.path.join(temp_dir, "log", log_name)
    stdin, stdout = os.popen2("tail -n "+ str(n) + " " + f)
    stdin.close()
    lines = "\n".join(stdout.readlines())
    stdout.close()
    return lines


def main(argv):
    tar_file_name, max_height = read_argv(argv)
    temp_dir = tempfile.mkdtemp()
    print("Tar name: " + tar_file_name)
    extract_tarball(tar_file_name, temp_dir)
    start_node(temp_dir)
    time.sleep(2)
    node = ExternalApi(ApiClient(host='localhost:3013/v1'))
    height = 0
    test_failed = False
    try:
        while height < max_height:
            time.sleep(5) # check every 5 seconds
            top = node.get_top() # node is alive and mining
            print("height=" + str(top.height) + "/" + str(max_height))
            height = max(top.height, height)
    except ApiException as e:
        test_failed = True
        print("node died")
    except urllib3.exceptions.MaxRetryError as e:
        test_failed = True
        print("node died")
    stop_node(temp_dir)
    if test_failed:
        print("Logs:")
        print(tail_logs(temp_dir, "epoch.log"))
    shutil.rmtree(temp_dir)
    if test_failed:
        sys.exit("FAILED")	

if __name__ == "__main__":
    main(sys.argv)
