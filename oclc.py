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
import os, sys
import yaml
import json

TEST_MODE= True
APP      = 'oclc'
YAML     = 'epl_oclc.yaml'
VERSION  = '0.00.01_dev'
# TODO: Define workflow for comparing OCLC numbers at a library against OCLC holdings.
# TODO: Load YAML
def usage():
    usage_text = f"""
    Usage: python {APP}.py [options]

    Performs local holdings updates at OCLC.

    This application uses YAML configurations found in {YAML}

    -y --yaml="/foo/bar.yaml": Specify a different yaml configuration file.
    -h: Prints this help message.
    -v: Turns on verbose messaging which reports errors and
      other diagnostic information.

    Version: {VERSION} Copyright (c) 2023.
    """
    sys.stderr.write(usage_text)
    sys.exit()

def _read_yaml_(yaml_file:str):
    """
    >>> c = _read_yaml_('epl_oclc.yaml')
    >>> print(c['OCLC']['institutionId'])
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
        except:
            sys.stderr.write(f"**error while reading YAML configurations from '{yaml_file}'.\n")
            sys.exit()

def main(argv):
    is_verbose = False
    yaml       = YAML
    try:
        opts, args = getopt.getopt(argv, "y:hv", ["yaml="])
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt in ("-y", "--yaml"):
            assert isinstance(arg, str)
            yaml = arg
        elif opt in "-h":
            usage()
        elif opt in "-v":
            is_verbose = True
    ##### End of cmd args.        
    config = _read_yaml_(yaml)

if __name__ == "__main__":
    if TEST_MODE == True:
        import doctest
        doctest.testmod()
    else:
        main(sys.argv[1:])
# EOF