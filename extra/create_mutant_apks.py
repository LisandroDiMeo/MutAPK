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


def process_mutant(mutant_id, mutant_folder, program_args, decompilation_path):
    mutant_folder_path = f"{program_args.mutants_path}/{mutant_folder}"
    mutated_file = os.listdir(mutant_folder_path)[0]
    mutated_file_path = f"{mutant_folder_path}/{mutated_file}"
    
    # copy the decompilation path content to the mutant output folder
    mutant_output_dir = program_args.output_dir + "/mutant-" + str(mutant_id)
    shutil.copytree(decompilation_path, mutant_output_dir)
    
    # find the file to change
    directories_to_search = glob.glob(mutant_output_dir + '/smali*')
    directories_to_search.append(mutant_output_dir + "/res/values")
    file_to_change_path = ""
    
    if mutated_file == "AndroidManifest.xml":
        file_to_change_path = mutant_output_dir + "/AndroidManifest.xml"
    else:
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

    print(f"> Compiling the mutant {mutant_id} APK...")
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
    print(f"> Compiling finished for mutant {mutant_id}")

    sign_apk(mutant_apk_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser for Creating Mutatant APKs")

    parser.add_argument('mutants_path', help='Path where the mutants are stored')
    parser.add_argument('output_dir', help='Output dir where the apk mutants will be stored')
    parser.add_argument('--apk_path', help='APK path')
    parser.add_argument('--apk_tool_path', help='APK Tool Path')
    parser.add_argument('--apk_signer_path', help='APK Signer Path')

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

    if not os.path.exists(args.apk_signer_path):
        print("APK Signer path does not exist")
        exit(1)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print("-> Starting to create mutant APKs")
    print("-> Mutants path: " + args.mutants_path)
    print("-> Output dir: " + args.output_dir)
    print("-> APK path: " + args.apk_path)
    print("-> APK Tool path: " + args.apk_tool_path)
    print("-> APK Signer path: " + args.apk_signer_path)

    mutant_folders = list(filter(lambda f: os.path.isdir(f"{args.mutants_path}/{f}"), os.listdir(args.mutants_path)))
    print(f"Found {len(mutant_folders)} mutants")
    
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
        for idx, mutant_folder in enumerate(mutant_folders):
            mutation_process = executor.submit(process_mutant, idx, mutant_folder, args, decompilation_path)