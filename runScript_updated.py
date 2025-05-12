from subprocess import call, Popen

# FIXME: low simRuns.txt is not generated, please fix that :(
# INFO: Yes did it :)

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
    for i in glob.glob(os.path.join(path, "*")):
        remove_thing(i)


def run_process(cmdList, loader, maxParallelProcess: int = 0):
    if maxParallelProcess != 0:
        jobsToRun = maxParallelProcess
    else:
        jobsToRun = maxProcess

    total_sims = len(cmdList) / 2
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
                if not "mkdir" in cCmd[0]:
                    cSim += 1
                    loader.stop()
                    loader = Loader(
                        f"[{cSim}]/[{total_sims}] Running sim {cCmd[9]} ...",
                        "Done!",
                        0.05,
                    ).start()
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
                    if not "mkdir" in cCmd[0]:
                        cSim += 1
                        loader.stop()
                        loader = Loader(
                            f"[{cSim}]/[{total_sims}] Running sim {cCmd[9]} ...",
                            "Done!",
                            0.05,
                        ).start()
                    procs.append(Popen(cCmd))

        except Exception as e:
            print("Subprocess error...")
            print(e)
            exit(-1)
    cmdList = []


def push_raw(_cmdList=[]):
    run_process(_cmdList, "", 1)


def push_commands(runMode="", configDict={}, outputDir=""):
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
            f"{outputDir}/{runMode}/{sysRunCfg}_runLog.txt "  # Enable logging
            f"lae "  # Run config
            f"-c {parallelCpus} "
            f"{model} "  # Application
            f"4096 "  # Number of GPUs
            f"4096 "  # Max batch size
            f"float16 "  # Data type
            f"{systemParams} "  # System
            f"{outputDir}/{runMode}/{sysRunCfg}_stats.csv"  # Output
        )

    elif runMode == "llm":
        model = configDict["model"]
        modelParams = configDict["modelParams"]
        systemParams = configDict["systemParams"]
        additionalArgs = configDict["extra"]
        sysRunCfg = configDict["sysCfg"]

        calculon_args = (
            f"-l "
            f"{outputDir}/runLog.txt "  # Enable logging
            f"llm "  # Run config
            f"{model} "  # Application
            f"{modelParams} "  # Execution configuraion
            f"{systemParams} "  # System
            f"{outputDir}/{runMode}/{sysRunCfg}_stats.json "  # Stats
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
            f"{outputDir}/{sysRunCfg}_runLog.txt "  # Enable logging
            f"loe "  # Run config
            f"{model} "  # Application
            f"4096 "  # Number of GPUs
            f"4096 "  # Max batch size
            f"float16 "  # Data type
            f"{systemParams} "  # System
            f"{outputDir}/{sysRunCfg}_output.json "  # Output
            "-c 4 "
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


def simGenerator(
    _cModel,
    _memCap,
    _memBW,
    _iChipBw,
    _iChipEff,
    _iiChipBW,
    _iiChipEff,
    _outputDir,
    _memName="",
    _intraName="",
    _interName="",
):
    cCfg = {
        "model": _cModel,
        "memCap": _memCap,
        "memBW": _memBW,
        "interChipBW": _iChipBw,
        "interChipEff": _iChipEff,
        "intraChipBW": _iiChipBW,
        "intraChipEff": _iiChipEff,
        "sysCfg": "",
        "output": _outputDir,
    }
    titleStr = (
        "tsmc_sow"
        + "_"
        + _memName
        + "_"
        + str(cCfg["memCap"])
        + "_"
        + str(cCfg["memBW"])
        + "_"
        + _intraName
        + "_"
        + str(cCfg["interChipBW"])
        + "_"
        + str(cCfg["interChipEff"])
        + "_"
        + _interName
        + "_"
        + str(cCfg["intraChipBW"])
        + "_"
        + str(cCfg["intraChipEff"])
        + ".json"
    )

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
    memoryType = [
        {
            "Name": "HBM2e",
            "Datarate": 4,
            "IO": 1024,
            "CapacityPerStack": 16,
            "Stacks": 4,
        },
        {
            "Name": "HBM3",
            "Datarate": 6.4,
            "IO": 1024,
            "CapacityPerStack": 24,
            "Stacks": 4,
        },
        {
            "Name": "HBM4",
            "Datarate": 8,
            "IO": 2048,
            "CapacityPerStack": 36,
            "Stacks": 4,
        },
        {
            "Name": "HBM5",
            "Datarate": 9.4,
            "IO": 2048,
            "CapacityPerStack": 48,
            "Stacks": 4,
        },
        # {"Name": "UCIe", "PerLaneBW": 4, "NrLanes": 1024}
        {
            "Name": "HBM2e",
            "Datarate": 4,
            "IO": 1024,
            "CapacityPerStack": 16,
            "Stacks": 8,
        },
        {
            "Name": "HBM3",
            "Datarate": 6.4,
            "IO": 1024,
            "CapacityPerStack": 24,
            "Stacks": 8,
        },
        {
            "Name": "HBM4",
            "Datarate": 8,
            "IO": 2048,
            "CapacityPerStack": 36,
            "Stacks": 8,
        },
        {
            "Name": "HBM5",
            "Datarate": 9.4,
            "IO": 2048,
            "CapacityPerStack": 48,
            "Stacks": 8,
        },
        # {"Name": "UCIe", "PerLaneBW": 4, "NrLanes": 1024}
        {
            "Name": "HBM2e",
            "Datarate": 4,
            "IO": 1024,
            "CapacityPerStack": 16,
            "Stacks": 12,
        },
        {
            "Name": "HBM3",
            "Datarate": 6.4,
            "IO": 1024,
            "CapacityPerStack": 24,
            "Stacks": 12,
        },
        {
            "Name": "HBM4",
            "Datarate": 8,
            "IO": 2048,
            "CapacityPerStack": 36,
            "Stacks": 12,
        },
        {
            "Name": "HBM5",
            "Datarate": 9.4,
            "IO": 2048,
            "CapacityPerStack": 48,
            "Stacks": 12,
        },
        # {"Name": "UCIe", "PerLaneBW": 4, "NrLanes": 1024}
        {
            "Name": "HBM2e",
            "Datarate": 4,
            "IO": 1024,
            "CapacityPerStack": 16,
            "Stacks": 16,
        },
        {
            "Name": "HBM3",
            "Datarate": 6.4,
            "IO": 1024,
            "CapacityPerStack": 24,
            "Stacks": 16,
        },
        {
            "Name": "HBM4",
            "Datarate": 8,
            "IO": 2048,
            "CapacityPerStack": 36,
            "Stacks": 16,
        },
        {
            "Name": "HBM5",
            "Datarate": 9.4,
            "IO": 2048,
            "CapacityPerStack": 48,
            "Stacks": 16,
        },
        # {"Name": "UCIe", "PerLaneBW": 4, "NrLanes": 1024}
    ]

    # This is for a single LVlink, and there are 12 in A100, 18 in H100
    # NVLink3, 4, 5, 6, C2C, HBI divding 10 TB into 6 lanes for FC
    interconnectType = [
        {"Name": "NVLink3", "PerLaneBW": 50, "NrLanes": 12},
        {"Name": "NVLink4", "PerLaneBW": 50, "NrLanes": 18},
        {"Name": "NVLink5", "PerLaneBW": 100, "NrLanes": 18},
        {"Name": "NVLink6", "PerLaneBW": 100, "NrLanes": 18},
        {"Name": "NVLink-C2C", "PerLaneBW": 200, "NrLanes": 10},
        {"Name": "NVLink-HBI", "PerLaneBW": 16384, "NrLanes": 6},
    ]

    ucie_datarates = [4, 8, 16, 32, 48, 64, 128]
    ucie_modules = [1, 2, 4, 8, 16, 32]
    for m in ucie_modules:
        for i in ucie_datarates:
            interconnectType.append(
                {"Name": f"UCIe-{i}", "PerLaneBW": i, "NrLanes": m * 128},
            )

    # INFO: Defaults: total mem capacity per GPU chiplet GB, mem IO datarate
    # (Gbps), mem IOs, interconnect BW (GBps)
    defaults = [
        64,
        {
            "Name": "HBM2e",
            "Datarate": 4,
            "IO": 1024,
            "CapacityPerStack": 16,
            "Stacks": 4,
        },
        {"Name": "NVLink3", "PerLaneBW": 50, "NrLanes": 12},
    ]

    # INFO: This is memory BW per GPU/chiplet in GBps

    # WARN: Old config list
    # memBW = [450, 1000, 1200, 1400, 1800, 2000]

    # WARN: Old config list
    # interChipletBW = [450, 900, 1000, 1350, 1800]
    # WARN: Old config list
    # intraChipletBW = [50, 100, 150, 300, 450, 900, 1000]

    # interChipLetEff = [i/10 for i in range(1, 10, 1)]
    # intraChipletEff =[i/10 for i in range(1, 10, 1)]

    # memPerStack = [16]
    # interChipletBW = [900]
    interChipLetEff = [0.65]
    # intraChipletBW = [100]
    intraChipletEff = [0.9]

    loader = Loader(
        "Cleaning ./systems/test/ for old configs...", "Done!", 0.05
    ).start()
    empty_directory("./systems/test")
    loader.stop()
    simRuns = []

    # Sensitivity
    defaultConfigs = [64, 4192, 450, 0.65, 450, 0.9]
    senMemCap = []
    senMemBW = []
    seniBW = []
    seniEff = []
    seniiBW = []
    seniiEff = []
    loeSims = []

    # for _cModel in models:
    # loader = Loader(
    #     "Preparing sensitivity sims for memory capacity...", "Done!", 0.05
    # ).start()
    # for _memCap in memoryType:
    #     senMemCap.append(
    #         simGenerator(
    #             _cModel,
    #             int(_memCap["CapacityPerStack"] * _memCap["Stacks"]),
    #             int(_memCap["Datarate"] * _memCap["IO"]),
    #             defaultConfigs[2],
    #             defaultConfigs[3],
    #             defaultConfigs[4],
    #             defaultConfigs[5],
    #             f"testRuns/sensitivity/memorySweep",
    #             _memCap["Name"],
    #             "NVLink3",
    #             "NVLink3",
    #         )
    #     )
    # loader.stop()
    # loader = Loader(
    #     "Preparing sensitivity sims for inter chiplet BW ...", "Done!", 0.05
    # ).start()
    #
    # for cInterconnect in interconnectType:
    #     seniBW.append(
    #         simGenerator(
    #             _cModel,
    #             defaultConfigs[0],
    #             defaultConfigs[1],
    #             int(cInterconnect["PerLaneBW"] * cInterconnect["NrLanes"]),
    #             defaultConfigs[3],
    #             defaultConfigs[4],
    #             defaultConfigs[5],
    #             f"testRuns/sensitivity/interChipletBW",
    #             "HBM3",
    #             cInterconnect["Name"],
    #             "NVLink3",
    #         )
    #     )
    #
    # loader.stop()
    # loader = Loader(
    #     "Preparing sensitivity sims for inter chiplet efficiency ...", "Done!", 0.05
    # ).start()
    #
    # for _iChipEff in interChipLetEff:
    #     seniEff.append(
    #         simGenerator(
    #             _cModel,
    #             defaultConfigs[0],
    #             defaultConfigs[1],
    #             defaultConfigs[2],
    #             _iChipEff,
    #             defaultConfigs[4],
    #             defaultConfigs[5],
    #             f"testRuns/sensitivity/interChipLetEff",
    #             "HBM3",
    #             "NVLink3",
    #             "NVLink3",
    #         )
    #     )
    #
    # loader.stop()
    # loader = Loader(
    #     "Preparing sensitivity sims for intra chiplet BW ...", "Done!", 0.05
    # ).start()
    #
    # for cInterconnect in interconnectType:
    #     seniiBW.append(
    #         simGenerator(
    #             _cModel,
    #             defaultConfigs[0],
    #             defaultConfigs[1],
    #             defaultConfigs[2],
    #             defaultConfigs[3],
    #             int(cInterconnect["PerLaneBW"] * cInterconnect["NrLanes"]),
    #             defaultConfigs[5],
    #             f"testRuns/sensitivity/intraChipletBW",
    #             "HBM3",
    #             "NVLink3",
    #             cInterconnect["Name"],
    #         )
    #     )
    #
    # loader.stop()
    # loader = Loader(
    #     "Preparing sensitivity sims for intra chiplet efficiency ...", "Done!", 0.05
    # ).start()
    #
    # for _iiChipEff in interChipLetEff:
    #     seniiEff.append(
    #         simGenerator(
    #             _cModel,
    #             defaultConfigs[0],
    #             defaultConfigs[1],
    #             defaultConfigs[2],
    #             defaultConfigs[3],
    #             defaultConfigs[4],
    #             _iiChipEff,
    #             f"testRuns/sensitivity/intraChipletEff",
    #             "HBM3",
    #             "NVLink3",
    #             "NVLink3",
    #         )
    #     )
    #
    # loader.stop()

    loader = Loader("Preparing full sweep ...", "Done!", 0.05).start()
    for _cModel in models:
        for _memBW in memoryType:
            for _iChipBW in interconnectType:
                for _iChipEff in interChipLetEff:
                    for _iiChipBW in interconnectType:
                        for _iiChipEff in interChipLetEff:
                            loeSims.append(
                                simGenerator(
                                    _cModel,
                                    int(_memBW["CapacityPerStack"] * _memBW["Stacks"]),
                                    int(_memBW["Datarate"] * _memBW["IO"]),
                                    int(_iChipBW["PerLaneBW"] * _iChipBW["NrLanes"]),
                                    _iChipEff,
                                    int(_iiChipBW["PerLaneBW"] * _iiChipBW["NrLanes"]),
                                    _iiChipEff,
                                    "testRuns/loe",
                                    _memBW["Name"],
                                    _iChipBW["Name"],
                                    _iiChipBW["Name"],
                                )
                            )

    loader.stop()

    loader = Loader("Preparing parallel call buffer ...", "Done!", 0.05).start()

    for cRun in simRuns:
        cModel = cRun["model"]
        outputDir = "testRuns"
        outputDir = cRun["output"]

        push_commands(
            "loe",
            {
                "model": f"models/{cModel}.json",
                "procs": 4096,
                "batchSize": 4096,
                "systemParams": "systems/test/" + cRun["sysCfg"],
                "sysCfg": cRun["sysCfg"],
                "extra": "",
            },
            f"{outputDir}",
        )

    loader.stop()

    loader = Loader("Running sims ...", "Done!", 0.05).start()

    run_process(cmdList, loader, 1)

    loader.stop()

    loader = Loader("Saving sinRuns list ...", "Done!", 0.05).start()

    # with open(f"./testRuns/sensitivity/memorySweep/simRuns.txt", "w") as _file:
    #     _file.writelines("\n".join(senMemCap))
    # with open(f"./testRuns/sensitivity/interChipletBW/simRuns.txt", "w") as _file:
    #     _file.writelines("\n".join(seniBW))
    # with open(f"./testRuns/sensitivity/interChipLetEff/simRuns.txt", "w") as _file:
    #     _file.writelines("\n".join(seniEff))
    # with open(f"./testRuns/sensitivity/intraChipletBW/simRuns.txt", "w") as _file:
    #     _file.writelines("\n".join(seniiBW))
    # with open(f"./testRuns/sensitivity/intraChipletBW/simRuns.txt", "w") as _file:
    #     _file.writelines("\n".join(seniiEff))
    with open(f"./testRuns/loe/simRuns.txt", "w") as _file:
        _file.writelines("\n".join(loeSims))

    loader.stop()
