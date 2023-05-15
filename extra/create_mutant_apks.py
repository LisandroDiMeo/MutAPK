#!/usr/bin/python3 -u
import argparse
import glob
import os
import subprocess
import concurrent.futures
import tempfile
import shutil


def sign_apk(apk, mutant_log_file):
    mutant_log_file.write(f'Signing APK: {apk}\n')

    build_tools_dir = os.environ["ANDROID_HOME"] + "/build-tools/31.0.0/"
    zip_align_command = [build_tools_dir + "zipalign", "-p", "4", apk, str(apk) + ".aligned"]
    mutant_log_file.write(f'Running command: {zip_align_command}\n')
    subprocess.run(zip_align_command, stdout=mutant_log_file, stderr=mutant_log_file)

    # there is a bug with zipalign, we need two iterations, see:
    # https://stackoverflow.com/questions/38047358/zipalign-verification-failed-resources-arsc-bad-1
    zip_align_command = [build_tools_dir + "zipalign", "-f", "-p", "4", str(apk) + ".aligned", str(apk) + ".aligned2"]
    mutant_log_file.write(f'Running command: {zip_align_command}\n')
    subprocess.run(zip_align_command, stdout=mutant_log_file, stderr=mutant_log_file)

    os.remove(str(apk) + ".aligned")
    os.rename(str(apk) + ".aligned2", apk)

    android_home = os.environ["HOME"] + "/.android"

    # Assign the ANDROID_EMULATOR_HOME environment variable to android_home variable if it exists
    if "ANDROID_EMULATOR_HOME" in os.environ:
        android_home = os.environ["ANDROID_EMULATOR_HOME"]

    debug_keystore_path = os.path.join(android_home, "debug.keystore")
    mutant_log_file.write("Using debug keystore: " + debug_keystore_path + "\n")

    sign_apk_command = [build_tools_dir + "apksigner", "sign", "--ks", debug_keystore_path,
                        "--ks-key-alias", "androiddebugkey", "--ks-pass", "pass:android",
                        "--key-pass", "pass:android", apk]

    mutant_log_file.write(f'Running command: {sign_apk_command}\n')
    subprocess.run(sign_apk_command)

    os.remove(str(apk) + ".idsig")


def process_mutant(mutant_id, mutant_folder_path, mutated_file_path_in_decompilation_folder, mutant_type, program_args, decompilation_path):
    process_mutant_log_path = program_args.output_dir + f"/mutant-{str(mutant_id)}.log"
    
    print(f"Processing mutant {mutant_id}, log file: {process_mutant_log_path}")
    
    with open(process_mutant_log_path, "w") as process_mutant_log:
      try:
            process_mutant_log.write(f"Started mutant {mutant_id}...\n")
            
            mutant_output_dir = program_args.output_dir + "/mutant-" + str(mutant_id)
            process_mutant_log.write(f"Mutant output dir for mutant {mutant_id}: {mutant_output_dir}\n")

            if not os.path.exists(mutant_output_dir):
                os.makedirs(mutant_output_dir)

            # copy the decompilation path content to the mutant output folder
            process_mutant_log.write(f"Copying decompilation path content to the mutant output folder for mutant {mutant_id}\n")
            mutant_decompilation_dir = mutant_output_dir + "/mutant-decompilation"
            
            process_mutant_log.write(f"Source decompilation path for mutant {mutant_id}: {decompilation_path}\n")
            process_mutant_log.write(f"Mutant decompilation dir for mutant {mutant_id}: {mutant_decompilation_dir}\n")
            shutil.copytree(decompilation_path, mutant_decompilation_dir)
                
            # override the file that was mutated in the mutant output dir
            dest_file = os.path.join(mutant_decompilation_dir, mutated_file_path_in_decompilation_folder)
            mutated_file = os.listdir(mutant_folder_path)[0]
            mutated_file_path = f"{mutant_folder_path}/{mutated_file}" # The path to the modified file
            
            process_mutant_log.write(f"Copying {mutated_file_path} to {dest_file} for mutant {mutant_id}\n")
            shutil.copyfile(mutated_file_path, dest_file)

            # Dump mutant_type in a file inside mutant_output_dir
            mutant_type_file_path = f"{mutant_output_dir}/mutant_type.txt"
            process_mutant_log.write(f"Dumping mutant type to {mutant_type_file_path} for mutant {mutant_id}\n")
            with open(mutant_type_file_path, "w") as mutant_type_file:
                mutant_type_file.write(mutant_type)

            process_mutant_log.write(f"Compiling APK for mutant {mutant_id}\n")
            mutant_apk_path = mutant_output_dir + "/" + os.path.basename(program_args.apk_path)
            apktool_result = subprocess.run([
                "java",
                "-jar",
                args.apk_tool_path,
                "b",
                mutant_decompilation_dir,
                "-o",
                mutant_apk_path,
                "-f"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process_mutant_log.write(f"Compiling finished for mutant {mutant_id}\n")

            # Dump apktool output to a file inside mutant_output_idr
            apktool_output = apktool_result.stdout.decode("utf-8")
            apktool_compile_log_path = f"{mutant_output_dir}/apktool_compile_mutant_apk.log"
            process_mutant_log.write(f"Dumping apktool compile output to {apktool_compile_log_path}\n")
            with open(apktool_compile_log_path, "w") as apktool_compile_log:
                apktool_compile_log.write(apktool_output)

            if not os.path.exists(mutant_apk_path):
                process_mutant_log.write(f"APK file not found for mutant {mutant_id}\n")
                return

            sign_apk(mutant_apk_path, process_mutant_log)

            print("Mutant APK successfully created for mutant " + str(mutant_id))
            process_mutant_log.write("Mutant APK successfully created for mutant " + str(mutant_id) + "\n")
      except Exception as e:
          print(f"Error for mutant {mutant_id}")
          process_mutant_log.write(f"Error for mutant {mutant_id}: {e}\n")

    print(f"Finished processing mutant {mutant_id}")

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

    files_mutated = {}
    mutants_type = {}
    with open(mutants_log_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "Mutant " in line:
                parts = line.split(" ")
                mutant_id = int(parts[1][:-1])

                # Calculate the file mutated
                raw_str = parts[2]
                mutated_file_path = raw_str.split("//")[2][:-1]
                files_mutated[mutant_id] = mutated_file_path

                mutants_type[mutant_id] =  parts[3]
    
    print("Files mutated per mutant:")
    for mutant_id in files_mutated:
        print(f"-> Mutant {mutant_id}: {files_mutated[mutant_id]}")

    print("Decompiling APK...")
    decompilation_path = os.path.join(args.output_dir, "original-apk-decompilation")
    os.mkdir(decompilation_path)
    print(f"-> Decompilation path: {decompilation_path}")

    decompilation_result = subprocess.run([
        "java",
        "-jar",
        args.apk_tool_path,
        "d",
        args.apk_path,
        "-o",
        decompilation_path,
        "-f"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("-> Decompilation finished!")

    # Dump decompilation output to a file inside output_dir/log
    decompilation_output = decompilation_result.stdout.decode("utf-8")
    with open(f"{args.output_dir}/apktool_decompile.log", "w") as f:
        f.write(decompilation_output)

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for idx, mutant_folder in enumerate(sorted(mutant_folders)):
            mutant_id = idx + 1
            if mutant_id not in files_mutated:
                print(f"Mutant {mutant_id} not found in mutants log file")
                # print all keys
                print("Keys in mutants log file:")
                for k in files_mutated:
                    print(f"-> {k}")
                exit(1)
            
            file_mutated = files_mutated[mutant_id]
            mutant_type = mutants_type[mutant_id]
            print("Sending job for mutant " + str(mutant_id) + " with folder " + mutant_folder + ", file mutated " + file_mutated + " and type " + mutant_type)
            mutation_process = executor.submit(process_mutant, mutant_id, mutant_folder, file_mutated, mutant_type, args, decompilation_path)