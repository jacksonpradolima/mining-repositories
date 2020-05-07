import os
import shutil

buildlogsdata = "/mnt/NAS/japlima/mining-repositories/data/buildlogs/"
buildlogsraw = "/mnt/NAS/japlima/mining-repositories/raw_data/buildlogs/"

if not os.path.exists(buildlogsdata):
    os.makedirs(buildlogsdata)


dir_list = next(os.walk(buildlogsraw))[1]

for d in dir_list:

    newdir = buildlogsdata+d
    olddir = buildlogsraw+d

    blj = "/buildlog-data-travis.json"
    blv = "/buildlog-data-travis.csv"

    if not os.path.exists(newdir):
        os.makedirs(newdir)

    print("[COPYING] FROM", olddir, "TO", newdir)

    shutil.copy2(olddir+blj, newdir+blj)
    shutil.copy2(olddir+blv, newdir+blv)
