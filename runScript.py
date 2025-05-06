from subprocess import call, Popen

cmdList = []
maxProcess = 4


def run_process(cmdList, maxParallelProcess: int = 0):
    if maxParallelProcess != 0:
        jobsToRun = maxParallelProcess
    else:
        jobsToRun = maxProcess

    while len(cmdList) > 0:
        tmpList = []
        procs = []

        for x in range(jobsToRun):
            if len(cmdList) > 0:
                cCmd = cmdList.pop(0)
                tmpList.append(cCmd)

                # print(f"{cCmd}\n\n")

        try:
            for i in tmpList:
                # print(i)
                procs.append(
                    Popen(i)  # ,
                    # shell=True,
                    # stdout=PIPE,
                    # stderr=PIPE,
                    # )
                )
            # print("Process pushed...\n\n")
            for p in procs:
                p.wait()
                out, err = p.communicate()
                errcode = p.returncode
                # if errcode != 2:
                #    print(f"Errorcode : {errcode} -> {err}")
                #    print(out)
                if len(cmdList) > 0:
                    cCmd = cmdList.pop(0)
                    procs.append(Popen(cCmd))

        except Exception as e:
            print("Subprocess error...")
            print(e)
            exit(-1)

def push_raw(_cmdList = []):
    cmdList.append(_cmdList)


def push_commands(runMode = "", configDict = {}, outputDir = ""):
    # Becareful with multiple lines, need to add a space between each arguments
    if runMode == "lae":
        model = configDict["model"]
        parallelCpus = configDict["cpus"]
        nrGPUs = configDict["procs"]
        maxBatchSize = configDict["batchSize"]
        systemParams = configDict["systemParams"]

        additionalArgs = configDict["extra"]

        calculon_args = (
            f"-l "
            f"{outputDir}/runLog.txt " # Enable logging
            f"lae " # Run config
            f"-c 1 "
            f"{model} " # Application 
            f"4096 " # Number of GPUs
            f"4096 " # Max batch size
            f"float16 " # Data type
            f"{systemParams} " # System
            f"{outputDir}/calculon_stats.csv" # Output
        )

    elif runMode == "llm":
        model = configDict["model"]
        modelParams = configDict["modelParams"]
        systemParams = configDict["systemParams"]
        additionalArgs = configDict["extra"]

        calculon_args = (
            f"-l "
            f"{outputDir}/runLog.txt " # Enable logging
            f"llm " # Run config
            f"{model} " # Application 
            f"{modelParams} " # Execution configuraion
            f"{systemParams} " # System
            f"{outputDir}/calculon_stats.json " # Stats 
            f"-l "
            f"-p {outputDir}/calculon_peers.json"
            # f"> {outputDir}/runLog.txt"
        )
    elif runMode == "loe"
        pass

    # calculonCall = "python calculon_bin.py"
    cCmd = ["python", "calculon_bin.py"]
    cCmd.extend(calculon_args.split(" "))
    print(cCmd)

    cmdList.append(cCmd)

from calculon.io import write_json_file, read_json_file

def genSystemConfigs():
    pass


if __name__ == "__main__":
    param = [1, 2, 4, 11, 26, 53, 128]

    for cModel in param:
        outputDir = "testRun"
        push_commands(
            f"models/Test-{cModel}T.json",
            "examples/4096_t8_p2_d256_mbs4_full.json",
            "systems/h100_80g_nvl8.json",
            f"{outputDir}",
        )
    
        push_raw(["python", "scripts/3dplot_ap.py",
                  f"{outputDir}/calculon_stats.json",
                  "-t", f"Test plot for {cModel}T model"])
        break
    

    run_process(cmdList, 1)
