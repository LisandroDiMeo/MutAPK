#!/usr/bin/python -u
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
apk_dirs = os.listdir(args.apk_paths)

if os.path.exists("./extra/mutants_generated"):
    print(" ====== Clearing previous results ======")
    subprocess.run(['rm', '-rf', './extra/mutants_generated'])

# Craete Directory to store the mutants.
subprocess.run(['mkdir', './extra/mutants_generated'], stdout=subprocess.PIPE)
for apk_dir in apk_dirs:
    # Create APK Dir to store the mutants
    print(f"Starting process of mutation for {apk_dir}")
    apk_name = apk_dir[:-4]
    subprocess.run(['mkdir', "./extra/mutants_generated/" + apk_name])
    properties = {
        "apkPath": f"./{args.apk_paths}/{apk_dir}",
        "appName": apk_name,
        "mutantsFolder": f"./extra/mutants_generated/{apk_name}/",
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
    with open(f"./extra/mutants_generated/{apk_name}/properties_{apk_name}.json", 'w') as f:
        json.dump(properties, f)
    print("About to run MutAPK...")
    subprocess.run(
        ['java', '-jar', args.jar_path, f"./extra/mutants_generated/{apk_name}/properties_{apk_name}.json"]
    )
