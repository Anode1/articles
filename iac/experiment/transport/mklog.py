import sys, os
# write a log of frames alice->carol (not for bob), 1 KB bodies, up to target bytes
path, target = sys.argv[1], int(sys.argv[2])
body = ("x"*1023)+"\n"
with open(path,"w") as f:
    size=0; epoch=1793000000
    while size<target:
        hdr=f"alice|carol|{epoch}|{len(body)}\n"
        f.write(hdr); f.write(body); f.write("\n")
        size+=len(hdr)+len(body)+1; epoch+=1
print(os.path.getsize(path))
