#!/usr/bin/python3 -u
import argparse
import glob
import os
import subprocess
import concurrent.futures

# Create arg parser for Smaling Mutants
parser = argparse.ArgumentParser(description="Argument parser for Smaling Mutants")

# define args
parser.add_argument('mutants_path', help='Path where the mutants are stored')
parser.add_argument('output_dir', help='Output dir where the apk mutants will be stored')
parser.add_argument('--apk_path', help='APK to baksmali -> mutate -> smali', default="./apk/me.anon.grow.apk")
parser.add_argument('--apk_tool_path', help='APK Tool Path', default="./extra")
parser.add_argument('--apk_signer_path', help='APK Signer Path', default="./extra")
parser.add_argument('--delete_non_signed', help='y/n to delete non signed apk', default="y")

args = parser.parse_args()

if not os.path.exists(args.mutants_path):
    print("> Path does not exists! Quitting...")
    exit(1)

paths = os.listdir(args.mutants_path)
paths = list(filter(lambda f: os.path.isdir(f"{args.mutants_path}/{f}"), paths))

baksmali_apk_path = f"{args.output_dir}/temp"
subprocess.run(["mkdir", baksmali_apk_path])
print(f"> Running apk tool to baksmali {args.apk_path}")
subprocess.run([
    "java",
    "-jar",
    f"{args.apk_tool_path}/apktool.jar",
    "d",
    args.apk_path,
    "-o",
    f"{args.output_dir}/temp",
    "-f"])
print("> Baksmali finished!")


def process_mutant(mutant_id, file_path, program_args, baksmali_apk_path):
    mutated_file = os.listdir(f"./{program_args.mutants_path}/{file_path}")[0]
    mutated_file_path = f"./{program_args.mutants_path}/{file_path}/{mutated_file}"
    mutant_dir = program_args.output_dir + "/mutant-" + str(mutant_id)
    subprocess.run(["mkdir", mutant_dir])
    subprocess.run(["cp", "-R", baksmali_apk_path, mutant_dir])
    # find the file to change TODO: This only takes AST Changes, strings, colors and Manifest will be added
    directories_to_search = glob.glob(mutant_dir + '/temp/smali*')
    file_to_change_path = ""
    for directory in directories_to_search:
        file_pattern = "*" + mutated_file
        find_command = ["find", directory, "-type", "f", "-name", file_pattern]
        result = subprocess.run(find_command, stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        if len(output) > 0:
            file_to_change_path = output
            break
    print(f"The file to change for mutant {mutant_id} is at " + file_to_change_path)
    dir_of_file_to_change = os.path.dirname(file_to_change_path)
    # override the file and smali files
    subprocess.run(["cp", mutated_file_path, dir_of_file_to_change])
    print(f"> Smalling the mutant {mutant_id} apk...")
    subprocess.run([
        "java",
        "-jar",
        f"{program_args.apk_tool_path}/apktool.jar",
        "b",
        mutant_dir + "/temp",
        "-o",
        mutant_dir + "/" + os.path.basename(program_args.apk_path),
        "-f"])
    print(f"> Smalling finished for mutant {mutant_id}. Now signing it...")
    subprocess.run([
        "java",
        "-jar",
        f"{program_args.apk_tool_path}/uber-apk-signer.jar",
        "-a",
        mutant_dir + "/" + os.path.basename(program_args.apk_path)
    ])
    print(f"> Signing process for mutant {mutant_id} finished... ")
    if program_args.delete_non_signed == "y":
        print(f"> Removing non signed for mutant {mutant_id} apk...")
        subprocess.run(["rm", mutant_dir + "/" + os.path.basename(program_args.apk_path)])


with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    for idx, path in enumerate(paths):
        mutation_process = executor.submit(process_mutant, idx, path, args, baksmali_apk_path)

