# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from colorama import Fore, Style
from glob import glob
from .deploy import *
import json

def scan():

    # first look for requirements.txt and build the venv (add in set)
    deployments = set()
    packages = set()

    if not os.path.exists("actions.json"):
        return

    data = json.loads(open("actions.json").read())
    excluded = data["excluded"]

    reqs =  glob("packages/*/*/requirements.txt") + glob("packages/*/*/package.json")
    print("========== REQUIREMENT FILES ========== \n")
    for req in reqs:
        _req = req.rsplit("/",1)[0]
        skip = False # Used to skip a request if matched in the excluded list

        for excl in excluded:
            if _req.startswith(excl):
                skip = True
                print(f">> {req} is {Fore.RED}excluded{Style.RESET_ALL}, skipping update.")
                break

        if skip:
            continue # Skip req

        print(f">> {_req} is {Fore.LIGHTGREEN_EX}included{Style.RESET_ALL}, updating.")    
        sp = req.split("/")
        act = build_zip(sp[1],sp[2])
        deployments.add(act)
        packages.add(sp[1])


    mains = glob("packages/*/*/index.js") + glob("packages/*/*/__main__.py")
    print("========== MAIN FILES ========== \n")
    for main in mains: 
        skip = False

        for excl in excluded:
            if main.startswith(excl):
                skip = True
                print(f"> {main} is {Fore.RED}excluded{Style.RESET_ALL}, skipping update.")
                break

        if skip:
            continue # Skip main

        print(f"> {main} is {Fore.LIGHTGREEN_EX}included{Style.RESET_ALL}, updating.")    
        sp = main.split("/")
        act = build_action(sp[1],sp[2])
        deployments.add(act)
        packages.add(sp[1]) 
    

    singles = glob("packages/*/*.py") +  glob("packages/*/*.js")
    print("========== SINGLE FILES ========== \n")
    for single in singles:
        skip = False

        for excl in excluded:
            if single.startswith(excl):
                skip = True
                print(f">> {single} is {Fore.RED}excluded{Style.RESET_ALL}, skipping update.")
                break
        
        if skip: 
            continue # Skip single file
    
        print(f">> {single} is {Fore.LIGHTGREEN_EX}included{Style.RESET_ALL}, updating.")    
        sp = single.split("/")
        deployments.add(single)
        packages.add(sp[1])

    print(">>> Deploying:")

    for package in packages:
        print("%", package)
        deploy_package(package)
    
    for action in deployments:
        print("^", action)
        deploy_action(action)

