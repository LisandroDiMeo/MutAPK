#!/usr/bin/python3 -u
import argparse
import glob
import os
import subprocess
import concurrent.futures
import tempfile
import shutil


def sign_apk(apk):
    print(f'Signing APK: {apk}')

    build_tools_dir = os.environ["ANDROID_HOME"] + "/build-tools/31.0.0/"
    zip_align_command = [build_tools_dir + "zipalign", "-p", "4", apk, str(apk) + ".aligned"]
    print(f'Running command: {zip_align_command}')
    subprocess.run(zip_align_command)

    # there is a bug with zipalign, we need two iterations, see:
    # https://stackoverflow.com/questions/38047358/zipalign-verification-failed-resources-arsc-bad-1
    zip_align_command = [build_tools_dir + "zipalign", "-f", "-p", "4", str(apk) + ".aligned", str(apk) + ".aligned2"]
    print(f'Running command: {zip_align_command}')
    subprocess.run(zip_align_command)

    os.remove(str(apk) + ".aligned")
    os.rename(str(apk) + ".aligned2", apk)

    android_home = os.environ["HOME"] + "/.android"

    # Assign the ANDROID_EMULATOR_HOME environment variable to android_home variable if it exists
    if "ANDROID_EMULATOR_HOME" in os.environ:
        android_home = os.environ["ANDROID_EMULATOR_HOME"]

    debug_keystore_path = os.path.join(android_home, "debug.keystore")
    print("Using debug keystore: " + debug_keystore_path)

    sign_apk_command = [build_tools_dir + "apksigner", "sign", "--ks", debug_keystore_path,
                        "--ks-key-alias", "androiddebugkey", "--ks-pass", "pass:android",
                        "--key-pass", "pass:android", apk]

    print(f'Running command: {sign_apk_command}')
    subprocess.run(sign_apk_command)

    os.remove(str(apk) + ".idsig")


def process_mutant(mutant_id, mutant_folder, mutated_file_path_in_decompilation_folder, program_args, decompilation_path):
    print(f"Processing mutant {mutant_id}...")
    mutant_folder_path = f"{program_args.mutants_path}/{mutant_folder}"
    mutated_file = os.listdir(mutant_folder_path)[0]
    mutated_file_path = f"{mutant_folder_path}/{mutated_file}" # The path to the modified file
    
    # copy the decompilation path content to the mutant output folder
    mutant_output_dir = program_args.output_dir + "/mutant-" + str(mutant_id)
    shutil.copytree(decompilation_path, mutant_output_dir)
        
    # override the file that was mutated in the mutant output dir
    dest_file = os.path.join(mutant_output_dir, mutated_file_path_in_decompilation_folder)
    print(f"Copying {mutated_file_path} to {dest_file}")
    shutil.copyfile(mutated_file_path, dest_file)

    print(f"Compiling the mutant {mutant_id} APK...")
    mutant_apk_path = mutant_output_dir + "/" + os.path.basename(program_args.apk_path)
    subprocess.run([
        "java",
        "-jar",
        args.apk_tool_path,
        "b",
        mutant_output_dir,
        "-o",
        mutant_apk_path,
        "-f"])
    print(f"Compiling finished for mutant {mutant_id}")

    sign_apk(mutant_apk_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser for Creating Mutatant APKs")

    parser.add_argument('--mutants_path', help='Path where the mutants are stored')
    parser.add_argument('--output_dir', help='Output dir where the apk mutants will be stored')
    parser.add_argument('--apk_path', help='APK path')
    parser.add_argument('--apk_tool_path', help='APK Tool Path')

    args = parser.parse_args()

    # Validate arguments
    if not os.path.exists(args.mutants_path):
        print("Mutants path does not exist")
        exit(1)

    if not os.path.exists(args.apk_path):
        print("APK path does not exist")
        exit(1)
    
    if not os.path.exists(args.apk_tool_path):
        print("APK Tool path does not exist")
        exit(1)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print("-> Starting to create mutant APKs")
    print("-> Mutants path: " + args.mutants_path)
    print("-> Output dir: " + args.output_dir)
    print("-> APK path: " + args.apk_path)
    print("-> APK Tool path: " + args.apk_tool_path)

    mutants_path_listing = list(map(lambda file: f"{args.mutants_path}/{file}", os.listdir(args.mutants_path)))

    # Find mutant folders
    mutant_folders = list(filter(lambda f: os.path.isdir(f), mutants_path_listing))
    print(f"Found {len(mutant_folders)} mutants")
    for mutant_folder in mutant_folders:
        print(f"-> {mutant_folder}")

    # Find and parse mutants log file
    print("Parsing mutants log file")
    aux = list(filter(lambda f: os.path.isfile(f) and f.endswith("-mutants.log"), mutants_path_listing))
    if len(aux) == 0:
        print("Mutants log file not found")
        print(f"Files in mutants path: {args.mutants_path}")
        for file in mutants_path_listing:
            print(f"-> {file}")
        exit(1)

    mutants_log_file = aux[0]
    file_mutated_per_mutant_index = {}
    with open(mutants_log_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "Mutant " in line:
                parts = line.split(" ")
                mutant_index = int(parts[1][:-1])
                raw_str = parts[2]
                mutated_file_path = raw_str.split("//")[2][:-1]
                file_mutated_per_mutant_index[mutant_index] = mutated_file_path
    
    print("Files mutated per mutant:")
    for mutant_index in file_mutated_per_mutant_index:
        print(f"-> Mutant {mutant_index}: {file_mutated_per_mutant_index[mutant_index]}")

    print("Decompiling APK...")
    decompilation_path = tempfile.mkdtemp()
    print(f"-> Decompilation path: {decompilation_path}")

    subprocess.run([
        "java",
        "-jar",
        args.apk_tool_path,
        "d",
        args.apk_path,
        "-o",
        decompilation_path,
        "-f"])
    print("-> Decompilation finished!")

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for idx, mutant_folder in enumerate(sorted(mutant_folders)):
            file_mutated = file_mutated_per_mutant_index[str(idx + 1)]
            print("Sending job for mutant " + str(idx + 1) + " with folder " + mutant_folder + " and file mutated " + file_mutated)
            mutation_process = executor.submit(process_mutant, idx, mutant_folder, file_mutated, args, decompilation_path)

    # Clear decompliation path
    os.system("rm -rf " + decompilation_path)