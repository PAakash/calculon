import os, os.path
import json
import csv
import shutil

SHARE_DIR = "/imec/other/dtpatha/patel23/share"

dirToSearch = []
dirToSearch.append("./old_testRuns/sensitivity/memorySweep")
dirToSearch.append("./old_testRuns/sensitivity/interChipletBW")
dirToSearch.append("./old_testRuns/sensitivity/interChipLetEff")
dirToSearch.append("./old_testRuns/sensitivity/intraChipletBW")
dirToSearch.append("./old_testRuns/sensitivity/intraChipletBW")

# cDir = dirToSearch[0]
for cDir in dirToSearch:
    _tmpStrSplit = cDir.split("/")
    simType = _tmpStrSplit[2] + "_" + _tmpStrSplit[3]
    simList = cDir + "/simRuns.txt"
    simsToConbime = []

    with open(simList, "r") as _file:
        simsToConbime = _file.readlines()

    _data = []
    for cSim in simsToConbime:
        systemPath = cSim.split("/")[-1]
        systemPath = systemPath.replace(".json", "")
        systemPath = systemPath.replace("\n", "")
        # print(systemPath)

        try:
            splitStr = systemPath.split("_")
            cData = {
                "Sim": systemPath,
                "System": splitStr[0] + "_" + splitStr[1],
                "Memory": splitStr[2],
                "Mem Capacity": splitStr[3],
                "Mem BW": splitStr[4],
                "IntraChiplet": splitStr[5],
                "IntraChiplet BW": splitStr[6],
                "IntraChiplet Eff": splitStr[7],
                "InterChiplet": splitStr[8],
                "InterChiplet BW": splitStr[9],
                "InterChiplet Eff": splitStr[10],
            }

            statFile = cDir + "/" + systemPath + "_output.json"
            # print(statFile)

            with open(statFile, mode="r", encoding="utf-8") as read_file:
                jsonObj = json.load(read_file)
                for key, value in jsonObj["0"]["stats"].items():
                    cData[key] = value

            _data.append(cData)
        except Exception as e:
            print("Simething was off ...")
            print(e)

    with open(f"{cDir}/stats.csv", "w", newline="") as csvfile:
        fieldnames = _data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(_data)

    destFile = f"{SHARE_DIR}/calculon/{simType}.csv"
    shutil.copy(f"{cDir}/stats.csv", destFile)


# TODO: For loe simRuns is not generated :(
# WARN: If you are going to run another sim then please fix that
cDir = "./old_testRuns/loe"
simsToConbime = []
simType = "loe"

with open(f"{cDir}/simRuns.txt", "r") as _file:
    simsToConbime = _file.readlines()

_data = []
for cSim in simsToConbime:
    systemPath = cSim.split("/")[-1]
    systemPath = systemPath.replace(".json", "")
    systemPath = systemPath.replace("\n", "")
    # print(systemPath)

    splitStr = systemPath.split("_")
    try:
        cData = {
            "Sim": systemPath,
            "System": splitStr[0] + "_" + splitStr[1],
            "Memory": splitStr[2],
            "Mem Capacity": splitStr[3],
            "Mem BW": splitStr[4],
            "IntraChiplet": splitStr[5],
            "IntraChiplet BW": splitStr[6],
            "IntraChiplet Eff": splitStr[7],
            "InterChiplet": splitStr[8],
            "InterChiplet BW": splitStr[9],
            "InterChiplet Eff": splitStr[10],
        }

        statFile = cDir + "/" + systemPath + "_output.json"
        # print(statFile)

        with open(statFile, mode="r", encoding="utf-8") as read_file:
            jsonObj = json.load(read_file)
            for key, value in jsonObj["0"]["stats"].items():
                cData[key] = value

        _data.append(cData)
    except Exception as e:
        print("Simething was off ...")
        print(e)

with open(f"{cDir}/stats.csv", "w", newline="") as csvfile:
    fieldnames = _data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(_data)

destFile = f"{SHARE_DIR}/calculon/{simType}.csv"
shutil.copy(f"{cDir}/stats.csv", destFile)
