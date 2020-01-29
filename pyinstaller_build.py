import os
import shlex

resources = [
    os.path.join("mahjong", "templates"),
]
# pyinstaller --add-data=mahjong\templates;mahjong\templates -c --onefile mahjong\tenhou_record_check.py

targets = [
    os.path.join("mahjong", "tenhou_record_check.py"),
    os.path.join("mahjong", "win_rate_demo.py"),
    os.path.join("mahjong", "universe_paifu_convert.py"),
]

resources_all = ' '.join(
    "--add-data={}".format(
        os.pathsep.join([res, res])
    ) for res in resources
)

for target in targets:
    command = "pyinstaller {res} -c --onefile {target}".format(res=resources_all, target=target)
    print("executing '{}'".format(command))
    os.system(command)
