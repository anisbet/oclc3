#!/usr/bin/env python3
###############################################################################
#
# Purpose: Update OCLC local holdings for a given library.
# Date:    Tue Jan 31 15:48:12 EST 2023
# Copyright 2023 Andrew Nisbet
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################
import os
import sys
import yaml
import getopt
from lib.oclcws import OclcService
# Make sure you set this to False in production.
DEFAULT_SERVER='Test'
TEST_MODE= True
# TEST_MODE= False
APP      = 'oclc'
YAML     = 'epl_oclc.yaml'
VERSION  = '0.00.01_dev'
# TODO: Define workflow for comparing OCLC numbers at a library against OCLC holdings.
# TODO: Manage authentication. See oclcws.py for more information.
def usage():
    usage_text = f"""
    Usage: python {APP}.py [options]

    Performs local holdings updates at OCLC.

    This application uses YAML configurations found in {YAML}

    Required yaml values:
    Test: 
        name:          "TEST_NAME"
        clientId:      "Test client id from OCLC"
        secret:        "Test secret"
        registryId:    "128807"
        principalId:   "hex string from OCLC Web Service Key management page"
        principalIdns: "urn:oclc:wms:da"
        institutionalSymbol: "OCPSB"
    Production: 
        name:          "PROD_NAME"
        clientId:      "Test client id from OCLC"
        secret:        "Test secret"
        registryId:    "Production registry ID (integer)"
        principalId:   "hex string"
        principalIdns: "urn:oclc:platform:[registryId]"
        institutionalSymbol: "ABC"
    OCLC:
        institutionalSymbol: "ABC"
        host:          "oauth.oclc.org"

    -h: Prints this help message.
    -n --num_file[/foo/bar.txt]: File containing OCLC numbers to check.
    -v: Turns on verbose messaging which reports errors and
      other diagnostic information.
    -s --server="Test|Production": Gets the configuration for either the Test or
      Production server from the yaml file.
    -y --yaml="/foo/bar.yaml": Specify a different yaml configuration file.

    Version: {VERSION} Copyright (c) 2023.
    """
    sys.stderr.write(usage_text)
    sys.exit()

# Given two lists, compute which numbers OCLC needs to add (or set), which they need to delete (unset)
# and which need no change.
# param:  oclcnum_file path to OCLC numbers they have on record. 
# param:  librarynums_file path to list of numbers library has.
# param:  reclaim bool turns OCLC list into remove all.
def _diff_(oclcnums:list, librarynums:list, reclaim:bool=False):
    """
    >>> olist = [1,2,3]
    >>> llist = [2,3,4]
    >>> l = _diff_(olist, llist)
    >>> print(l)
    {1: '-', 2: '', 3: '', 4: '+'}
    """
    ret_dict = {}
    for oclcnum in oclcnums:
        if oclcnum in librarynums:
            ret_dict[oclcnum] = ""
        else:
            ret_dict[oclcnum] = "-"
    for libnum in librarynums:
        if libnum in oclcnums:
            ret_dict[libnum] = ""
        else:
            ret_dict[libnum] = "+"
    return ret_dict

def _set_unset_(nums:dict, create_unset_list:bool=True) -> list:
    """
    >>> n = {1: '-', 2: '', 3: '', 4: '+'}
    >>> _set_unset_(n)
    [1]
    >>> _set_unset_(n, False)
    [4]
    >>> n = {1: '', 2: '', 3: '', 4: ''}
    >>> _set_unset_(n)
    []
    >>> n = {1: '', 2: None, 3: '', 4: ''}
    >>> _set_unset_(n)
    []
    >>> n = {1: '', 2: None, 3: '+', 4: ''}
    >>> _set_unset_(n, False)
    [3]
    >>> n = {1: '', 2: None, 3: '', 4: ''}
    >>> _set_unset_(n, False)
    []
    """
    ret = []
    for item in nums.items():
        if item[1] == '-' and create_unset_list == True:
            ret.append(item[0])
        if item[1] == "+" and create_unset_list == False:
            ret.append(item[0])
    return ret

def _read_yaml_(yaml_file:str):
    """
    >>> c = _read_yaml_('epl_oclc.yaml')
    >>> print(c['OCLC']['institutionalSymbol'])
    CNEDM
    """
    if os.path.isfile(yaml_file) == False:
        sys.stderr.write(f"**error, no such YAML file '{yaml_file}'.\n")
        sys.exit()
    with open(yaml_file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def main(argv):
    verbose_mode     = False
    yaml             = YAML
    oclc_number_file = ''
    oclc_numbers     = []
    server           = DEFAULT_SERVER
    try:
        opts, args = getopt.getopt(argv, "hn:s:vy:", ["num_file=", "server=", "yaml="])
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt in "-h":
            usage()
        elif opt in ("-n", "--num_file"):
            assert isinstance(arg, str)
            if os.path.isfile(arg) == False:
                sys.stderr.write(f"*error, no such OCLC number list file: '{arg}'.\n")
                sys.exit()
            oclc_number_file = arg
            if verbose_mode:
                print(f"oclc number file list: {oclc_number_file}")
        elif opt in ("-s", "--server"):
            assert isinstance(arg, str)
            if arg == 'Test' or arg == 'Production':
                server = arg
            else:
                print(f"*error, '{arg}' is not a valid server. See -h for more information.")
                usage()
            if verbose_mode:
                print(f"server: {server}")
        elif opt in "-v":
            verbose_mode = True
            print(f"verbose mode {verbose_mode}")
        elif opt in ("-y", "--yaml"):
            assert isinstance(arg, str)
            yaml = arg
    ##### End of cmd args.        
    config = _read_yaml_(yaml)[server]
    if verbose_mode:
        print(f"config: '{config['name']}'")
    # Read in a list of OCLC numbers if provided.
    if oclc_number_file != '':
        with open(oclc_number_file, encoding='utf8') as f:
            for line in f:
                oclc_numbers.append(line.strip())
        f.close()
    if verbose_mode and oclc_number_file != '':
        print(f"OCLC numbers: {oclc_numbers}")
    print(f"config is a {type(config)} :: {config}")
    # Don't do anything if the input list is empty. 
    # TODO: Fix this so it isn't the only functions that run.
    if oclc_numbers:
        ws = OclcService(config)
        results = ws.check_control_numbers(oclc_numbers)
        print(f"result: {results[1]}")
        print(f"and the list now contains: {results[0]}")
    else:
        print(f"no oclc numbers read from file: '{oclc_number_file}'")

if __name__ == "__main__":
    if TEST_MODE == True:
        import doctest
        doctest.testmod()
    else:
        main(sys.argv[1:])
# EOF