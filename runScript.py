from subprocess import call, Popen

cmdList = []
maxProcess = 4

import os, os.path
import glob
import shutil

def remove_thing(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def empty_directory(path):
    for i in glob.glob(os.path.join(path, '*')):
        remove_thing(i)

def run_process(cmdList, loader, maxParallelProcess: int = 0):
    if maxParallelProcess != 0:
        jobsToRun = maxParallelProcess
    else:
        jobsToRun = maxProcess

    total_sims = len(cmdList)
    cSim = 0
    # loader = Loader("Running sims ...", "Done!", 0.05).start()
    # loader.desc = f"Running sims [{cSim}]/[{total_sims}] ..."

    while len(cmdList) > 0:
        tmpList = []
        procs = []

        for x in range(jobsToRun):
            if len(cmdList) > 0:
                cCmd = cmdList.pop(0)
                tmpList.append(cCmd)
                cSim += 1
                if not "mkdir" in cCmd[0]:
                    loader.stop()
                    loader = Loader(f"[{cSim}]/[{total_sims}] Running sim {cCmd[9]} ...", "Done!", 0.05).start()
                # loader.desc = f"Running sims ] ..."

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
                    cSim += 1
                    if not "mkdir" in cCmd[0]:
                        loader.stop()
                        loader = Loader(f"[{cSim}]/[{total_sims}] Running sim {cCmd[9]} ...", "Done!", 0.05).start()
                    procs.append(Popen(cCmd))

        except Exception as e:
            print("Subprocess error...")
            print(e)
            exit(-1)
    cmdList = []

def push_raw(_cmdList = []):
    run_process(_cmdList,"", 1)

def push_commands(runMode = "", configDict = {}, outputDir = ""):
    # Becareful with multiple lines, need to add a space between each arguments
    if runMode == "lae":
        model = configDict["model"]
        parallelCpus = configDict["cpus"]
        nrGPUs = configDict["procs"]
        maxBatchSize = configDict["batchSize"]
        systemParams = configDict["systemParams"]
        sysRunCfg = configDict["sysCfg"]
        sysRunCfg = sysRunCfg.replace(".json", "")

        additionalArgs = configDict["extra"]

        calculon_args = (
            f"-l "
            f"{outputDir}/{runMode}/{sysRunCfg}_runLog.txt " # Enable logging
            f"lae " # Run config
            f"-c {parallelCpus} "
            f"{model} " # Application 
            f"4096 " # Number of GPUs
            f"4096 " # Max batch size
            f"float16 " # Data type
            f"{systemParams} " # System
            f"{outputDir}/{runMode}/{sysRunCfg}_stats.csv" # Output
        )

    elif runMode == "llm":
        model = configDict["model"]
        modelParams = configDict["modelParams"]
        systemParams = configDict["systemParams"]
        additionalArgs = configDict["extra"]
        sysRunCfg = configDict["sysCfg"]

        calculon_args = (
            f"-l "
            f"{outputDir}/runLog.txt " # Enable logging
            f"llm " # Run config
            f"{model} " # Application 
            f"{modelParams} " # Execution configuraion
            f"{systemParams} " # System
            f"{outputDir}/{runMode}/{sysRunCfg}_stats.json " # Stats 
            # f"-l " # Log stats for all layers
            f"-p {outputDir}/{runMode}/{sysRunCfg}_peers.json"
        )
    elif runMode == "loe":
        # models/turing-530B.json 5128 2520 float16 systems/a100_80g.json output.json -m
        model = configDict["model"]
        nrGPUs = configDict["procs"]
        maxBatchSize = configDict["batchSize"]
        systemParams = configDict["systemParams"]
        sysRunCfg = configDict["sysCfg"]
        sysRunCfg = sysRunCfg.replace(".json", "")

        additionalArgs = configDict["extra"]

        calculon_args = (
            f"-l "
            f"{outputDir}/{sysRunCfg}_runLog.txt " # Enable logging
            f"loe " # Run config
            f"{model} " # Application 
            f"4096 " # Number of GPUs
            f"4096 " # Max batch size
            f"float16 " # Data type
            f"{systemParams} " # System
            f"{outputDir}/{sysRunCfg}_output.json " # Output
            "-m"
        )


    # calculonCall = "python calculon_bin.py"

    cCmd = ["mkdir", "-p", f"{outputDir}/{runMode}"]
    cmdList.append(cCmd)
    cCmd = ["python", "calculon_bin.py"]
    cCmd.extend(calculon_args.split(" "))
    # print(cCmd)

    cmdList.append(cCmd)

from calculon.io import write_json_file, read_json_file

def genSystemConfigs(config):
    # config = {
    #     "memCap": _memCap,
    #     "interChipBW": _iChipBW,
    #     "interChipEff": _iChipEff,
    #     "intraChipBW": _iiChipBW,
    #     "intraChipEff": _iiChipEff,
    # }
    baseConfigs = read_json_file("systems/h100_base.json")
    baseConfigs["mem1"]["GiB"] = int(config["memCap"])
    baseConfigs["mem1"]["GBps"] = int(config["memBW"])

    baseConfigs["networks"][0]["bandwidth"] = int(config["interChipBW"])
    baseConfigs["networks"][0]["size"] = 4
    baseConfigs["networks"][0]["efficiency"] = float(config["interChipEff"])

    baseConfigs["networks"][1]["bandwidth"] = int(config["intraChipBW"])
    baseConfigs["networks"][1]["efficiency"] = float(config["intraChipEff"])

    titleStr = config["sysCfg"]
    write_json_file(baseConfigs, f"systems/test/{titleStr}")
    return f"systems/test/{titleStr}"

def simGenerator(_cModel, _memCap, _memBW, _iChipBw, _iChipEff, _iiChipBW,
                 _iiChipEff, _outputDir):

    cCfg = {
        "model": _cModel,
        "memCap":_memCap,
        "memBW":_memBW,
        "interChipBW":_iChipBw,
        "interChipEff":_iChipEff,
        "intraChipBW":_iiChipBW,
        "intraChipEff":_iiChipEff,
        "sysCfg": "",
        "output":_outputDir,
    }
    titleStr = "tsmc_sow" + "_" + str(cCfg["memCap"]) + "_" + str(cCfg["memBW"]) + "_" + str(cCfg["interChipBW"]) + "_" + str(cCfg["interChipEff"]) + "_" + str(cCfg["intraChipBW"]) + "_" + str(cCfg["intraChipEff"]) + ".json"
    cCfg["sysCfg"] = titleStr
    simRuns.append(cCfg)
    return genSystemConfigs(cCfg)

from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep


class Loader:
    def __init__(self, desc="Loading...", end="Done!", timeout=0.1):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{self.end}: {self.desc}", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()

if __name__ == "__main__":
    # models = [1, 2, 4, 11, 26, 53, 128]
    models = ["turing-530B"]
    memPerStack = [12, 16, 20, 24, 28, 32]
    memBW = [450, 1000, 1200, 1400, 1800, 2000]
    interChipletBW = [450, 900, 1000, 1350, 1800]
    # interChipLetEff = [i/10 for i in range(1, 10, 1)]
    intraChipletBW = [50, 100, 150, 300, 450, 900, 1000]
    # intraChipletEff =[i/10 for i in range(1, 10, 1)] 

    # memPerStack = [16]
    # interChipletBW = [900]
    interChipLetEff = [0.65]
    # intraChipletBW = [100]
    intraChipletEff =[0.9] 

    memCap = []
    for _memPerStack in memPerStack:
        memCap.append(int(4 * _memPerStack))

    loader = Loader("Cleaning ./systems/test/ for old configs...", "Done!", 0.05).start()
    # push_raw(["rm", "-rf", "./systems/test/*"])
    empty_directory("./systems/test")
    loader.stop()
    # push_raw(["rm", "-rf", "./systems/test/*"])
    # sys.exit(0)
    simRuns = []

    # Sensitivity
    defaultConfigs = [16, 3072, 450, 0.65, 50, 0.9]
    senMemCap = []
    senMemBW = []
    seniBW = []
    seniEff = []
    seniiBW = []
    seniiEff = []
    for _cModel in models:
        loader = Loader("Preparing sensitivity sims for memory capacity...", "Done!", 0.05).start()
        for _memCap in memCap:
            senMemCap.append(simGenerator(_cModel, 
                         _memCap, 
                         defaultConfigs[1], 
                         defaultConfigs[2], 
                         defaultConfigs[3], 
                         defaultConfigs[4], 
                         defaultConfigs[5],
                         f"testRuns/sensitivity/memoryCapacity")
            )
        loader.stop()
        loader = Loader("Preparing sensitivity sims for memory bandwidth...", "Done!", 0.05).start()

        for _memBW in memBW:
            senMemBW.append(simGenerator(_cModel, 
                             defaultConfigs[0], 
                             _memBW, 
                             defaultConfigs[2], 
                             defaultConfigs[3], 
                             defaultConfigs[4], 
                             defaultConfigs[5],
                             f"testRuns/sensitivity/memoryBW"))

        loader.stop()
        loader = Loader("Preparing sensitivity sims for inter chiplet BW ...", "Done!", 0.05).start()

        for _iChipBW in interChipletBW:
            seniBW.append(simGenerator(_cModel, 
                         defaultConfigs[0], 
                         defaultConfigs[1], 
                         _iChipBW, 
                         defaultConfigs[3], 
                         defaultConfigs[4], 
                         defaultConfigs[5],
                         f"testRuns/sensitivity/interChipletBW"))

        loader.stop()
        loader = Loader("Preparing sensitivity sims for inter chiplet efficiency ...", "Done!", 0.05).start()

        for _iChipEff in interChipLetEff:
            seniEff.append(simGenerator(_cModel, 
                         defaultConfigs[0], 
                         defaultConfigs[1], 
                         defaultConfigs[2], 
                         _iChipEff, 
                         defaultConfigs[4], 
                         defaultConfigs[5],
                         f"testRuns/sensitivity/interChipLetEff"))

        loader.stop()
        loader = Loader("Preparing sensitivity sims for intra chiplet BW ...", "Done!", 0.05).start()

        for _iiChipBW in intraChipletBW:
            seniiBW.append(simGenerator(_cModel, 
                         defaultConfigs[0], 
                         defaultConfigs[1], 
                         defaultConfigs[2], 
                         defaultConfigs[3], 
                         _iiChipBW, 
                         defaultConfigs[5],
                         f"testRuns/sensitivity/intraChipletBW"))

        loader.stop()
        loader = Loader("Preparing sensitivity sims for intra chiplet efficiency ...", "Done!", 0.05).start()

        for _iiChipEff in interChipLetEff:
            seniiEff.append(simGenerator(_cModel, 
                         defaultConfigs[0], 
                         defaultConfigs[1], 
                         defaultConfigs[2], 
                         defaultConfigs[3], 
                         defaultConfigs[4],
                         _iiChipEff, 
                         f"testRuns/sensitivity/intraChipletEff"))

        loader.stop()

    loader = Loader("Preparing full sweep ...", "Done!", 0.05).start()
    for _cModel in models:
        for _memCap in memCap:
            for _memBW in memBW:
                for _iChipBW in interChipletBW:
                    for _iChipEff in interChipLetEff:
                        for _iiChipBW in intraChipletBW:
                            for _iiChipEff in interChipLetEff:
                                simGenerator(_cModel, _memCap,
                                             _memBW, _iChipBW, _iChipEff, _iiChipBW, _iiChipEff, "testRuns/loe")
                                # cCfg = {
                                #     "model": _cModel,
                                #     "memCap":_memCap,
                                #     "memBW":_memBW,
                                #     "interChipBW":_iChipBW,
                                #     "interChipEff":_iChipEff,
                                #     "intraChipBW":_iiChipBW,
                                #     "intraChipEff":_iiChipEff,
                                #     "sysCfg": ""
                                # }
                                # titleStr = "tsmc_sow" + "_" + str(cCfg["memCap"]) + "_" + str(cCfg["memBW"]) + "_" + str(cCfg["interChipBW"]) + "_" + str(cCfg["interChipEff"]) + "_" + str(cCfg["intraChipBW"]) + "_" + str(cCfg["intraChipEff"]) + ".json"
                                # cCfg["sysCfg"] = titleStr
                                # simRuns.append(cCfg)
                                # genSystemConfigs(cCfg)
    
    loader.stop()

    loader = Loader("Preparing parallel call buffer ...", "Done!", 0.05).start()

    for cRun in simRuns:
        cModel = cRun["model"]
        outputDir = "testRuns"
        outputDir = cRun["output"]

        # push_commands("lae", 
        #               {
        #               "model": f"models/{cModel}.json",
        #               "cpus":4,
        #               "procs": 4096,
        #               "batchSize": 4096,
        #               "systemParams": "systems/test/" + cRun["sysCfg"],
        #               "sysCfg": cRun["sysCfg"],
        #               "extra": "",
        #               },f"{outputDir}")
        #
        # push_commands(
        #     "llm",
        #     {
        #         "model": f"models/{cModel}.json",
        #         "modelParams":"examples/4096_t8_p2_d256_mbs4_full.json",
        #         "systemParams":"systems/h100_80g_nvl8.json",
        #         "extra":"",
        #     },
        #     f"{outputDir}",
        # )

        push_commands("loe", 
                      {
                      "model": f"models/{cModel}.json",
                      "procs": 4096,
                      "batchSize": 4096,
                      "systemParams": "systems/test/" + cRun["sysCfg"],
                      "sysCfg": cRun["sysCfg"],
                      "extra": "",
                      },f"{outputDir}")
    
        # push_raw(["python", "scripts/3dplot_ap.py",
        #           f"{outputDir}/calculon_stats.json",
        #           "-t", f"Test plot for {cModel}T model"])

    loader.stop()

    loader = Loader("Running sims ...", "Done!", 0.05).start()

    run_process(cmdList, loader, 1)

    loader.stop()

    loader = Loader("Saving sinRuns list ...", "Done!", 0.05).start()

    with open(f"testRuns/sensitivity/memoryCapacity/simRuns.txt") as _file:
        _file.writelines("\n".join(senMemCap))
    with open(f"testRuns/sensitivity/memoryBW/simRuns.txt") as _file:
        _file.writelines("\n".join(senMemBW))
    with open(f"testRuns/sensitivity/interChipletBW/simRuns.txt") as _file:
        _file.writelines("\n".join(seniBW))
    with open(f"testRuns/sensitivity/interChipLetEff/simRuns.txt") as _file:
        _file.writelines("\n".join(seniEff))
    with open(f"testRuns/sensitivity/intraChipletBW/simRuns.txt") as _file:
        _file.writelines("\n".join(seniiBW))
    with open(f"testRuns/sensitivity/intraChipletBW/simRuns.txt") as _file:
        _file.writelines("\n".join(seniiEff))

    loader.stop()
