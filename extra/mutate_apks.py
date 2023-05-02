#!/usr/bin/python3 -u
import argparse
import json
import os
import subprocess

# create the parser object
parser = argparse.ArgumentParser(description='Argument Parse of Mutate APKs.')

# define the arguments
parser.add_argument('--jar-path', help='Path to MutAPK Jar.')
parser.add_argument('--apk-paths', help='Path where the apks are located')
parser.add_argument('--amount-mutants', help='Amount of mutants desired', default=10)

# parse the arguments
args = parser.parse_args()
amount_of_mutants = args.amount_mutants
apks_folder_path = args.apk_paths

if os.path.exists("./extra/mutants_generated"):
    print(" ====== Clearing previous results ======")
    subprocess.run(['rm', '-rf', './extra/mutants_generated'])

# Craete Directory to store the mutants.
subprocess.run(['mkdir', './extra/mutants_generated'], stdout=subprocess.PIPE)
for apk_file_name in os.listdir(apks_folder_path):
    # Create APK Dir to store the mutants
    print(f"Starting process of mutation for {apk_file_name}")
    apk_path = f"./{apks_folder_path}/{apk_file_name}"
    package_name = apk_file_name[:-4]
    
    app_mutants_folder = f"./extra/mutants_generated/{package_name}"
    subprocess.run(['mkdir', app_mutants_folder])

    properties = {
        "apkPath": apk_path,
        "appName": package_name,
        "mutantsFolder": app_mutants_folder,
        "operatorsDir": "./",
        "multithreadExec": "true",
        "shouldGenerateAPKs" : "false",
        "extraPath": "./extra",
        "selectionStrategy": "amountMutants",
        "selectionParameters": {
            "amountMutants": str(amount_of_mutants),
            "perOperator": "false",
            "confidenceLevel": "85",
            "marginError": "10",
            "baseAPKPath": "./"
        }
    }

    # Dump the properties to a json file.
    properties_path = f"{app_mutants_folder}/properties_{package_name}.json"
    with open(properties_path, 'w') as f:
        json.dump(properties, f)

    print("About to run MutAPK...")
    
    log_path = f"{app_mutants_folder}/mutapk_{package_name}.log"
    with open(log_path, 'w') as f:
        subprocess.run(['java', '-jar', args.jar_path, properties_path], stdout=f, stderr=f)
