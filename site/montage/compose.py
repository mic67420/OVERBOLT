import subprocess, os, sys
U="/root/.claude/uploads/4c8d8528-44e8-5d64-a3bd-288f4cee0e4d"
A=f"{U}/3499f5f5-VID_20261020_080824.mp4"; B=f"{U}/3963873f-VID_20261015_063516.mp4"; C=f"{U}/76019cf0-VID_20261015_061414.mp4"; PLATE=f"{U}/d5051a4d-image.jpg"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: print(" ".join(cmd)[:300]); print(r.stderr[-1800:]); sys.exit(1)
def tf(name,text):
    p=f"cap/{name}.txt"; open(p,"w",encoding="utf-8").write(text); return os.path.abspath(p)
def cap(name,text,t0,t1,y=210,size=78):
    return (f"drawtext=fontfile={FONT}:textfile={tf(name,text)}:fontsize={size}:fontcolor=white:borderw=6:bordercolor=black:"
            f"text_align=center:line_spacing=14:x=(w-text_w)/2:y={y}:box=1:boxcolor=black@0.5:boxborderw=26:enable='between(t,{t0},{t1})'")
def stopwatch(name,mult,y=1560,color="0xff3b30",label=None):
    t=f"%{{eif:floor(t*{mult}/60):d:2}}:%{{eif:mod(floor(t*{mult}),60):d:2}}"
    return (f"drawtext=fontfile={FONT}:textfile={tf(name,t)}:fontsize=170:fontcolor={color}:borderw=8:bordercolor=black:x=(w-text_w)/2:y={y}")
def fixed(name,text,y,color,size=170):
    return (f"drawtext=fontfile={FONT}:textfile={tf(name,text)}:fontsize={size}:fontcolor={color}:borderw=8:bordercolor=black:x=(w-text_w)/2:y={y}")
COVER="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
FIT="scale=-2:1920,pad=1080:1920:(ow-iw)/2:0:color=0x05070a,setsar=1"
def clip(out,src,ss,dur,speed,base,filters=(),extra_in=()):
    vf=[f"setpts=PTS/{speed}","fps=30",base]+list(filters)
    run(["ffmpeg","-v","error","-y","-ss",str(ss),"-t",str(dur),"-i",src,"-an","-vf",",".join(vf),"-t",f"{dur/speed:.3f}","-c:v","libx264","-preset","medium","-crf","21","-pix_fmt","yuv420p","-r","30",out])
def endcard(out,dur,l1,l2,l3):
    vf=(f"drawtext=fontfile={FONT}:textfile={tf('e1',l1)}:fontsize=92:fontcolor=white:x=(w-text_w)/2:y=520,"
        f"drawtext=fontfile={FONT}:textfile={tf('e2',l2)}:fontsize=70:fontcolor=0x2af5e0:text_align=center:line_spacing=16:x=(w-text_w)/2:y=760,"
        f"drawtext=fontfile={FONT}:textfile={tf('e3',l3)}:fontsize=56:fontcolor=0x9aa7b4:text_align=center:x=(w-text_w)/2:y=1260")
    run(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=0x05070a:s=1080x1920:r=30:d={dur}","-vf",vf,"-c:v","libx264","-crf","21","-pix_fmt","yuv420p",out])
def concat(parts,out):
    open("seg/list.txt","w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","seg/list.txt","-c:v","libx264","-preset","medium","-crf","22","-pix_fmt","yuv420p","-an","-movflags","+faststart",out])
END=("OVERBOLT | NO BS","5 € une seule fois.\nPas d'abonnement.\nPas une centrale\nnucléaire.","Adresse dans ma bio")
OV_VAL=os.path.abspath("ov_valider.mp4"); OV_PH=os.path.abspath("ov_photo.mp4"); OV_COL=os.path.abspath("ov_couleurs.mp4")

# ---------------- V1 : noter une série, ton appli vs Overbolt ----------------
clip("seg/v1a.mp4",A,0,21,3.0,COVER,[cap("v1a","NOTER UNE SÉRIE\nDANS TON APPLI :",0,7.0),stopwatch("v1sw",3.0,y=1700)])
clip("seg/v1b.mp4",OV_VAL,0.8,3.0,1.0,FIT,[cap("v1b","DANS OVERBOLT :\n1 TAP.",0,3.0),fixed("v1ok","00:01",1700,"0x34c759")])
endcard("seg/v1e.mp4",2.5,*END)
concat(["seg/v1a.mp4","seg/v1b.mp4","seg/v1e.mp4"],"V1_ton-appli-vs-overbolt.mp4")

# ---------------- V2 : le réglage de la machine ----------------
clip("seg/v2a.mp4",B,0,14.8,1.4,COVER,[cap("v2a1","TU RÈGLES\nTA MACHINE…",0,2.4),cap("v2a2","CRAN 6 ? CRAN 7 ?\nTU T'EN SOUVIENS\nDANS 3 SEMAINES ?",2.6,6.0),cap("v2a3","ET LA GOUPILLE ?\nLE BON POIDS ?",6.2,10.4)])
clip("seg/v2b.mp4",OV_PH,0.9,2.6,1.0,FIT,[cap("v2b","OVERBOLT : LA PHOTO\nDU RÉGLAGE EST DANS\nL'APPLI.",0,2.6,y=170)])
endcard("seg/v2e.mp4",2.5,*END)
concat(["seg/v2a.mp4","seg/v2b.mp4","seg/v2e.mp4"],"V2_reglage-machine.mp4")

# ---------------- V3 : charge max + couleurs ----------------
run(["ffmpeg","-v","error","-y","-loop","1","-framerate","30","-t","4","-i",PLATE,"-an","-vf",
 "scale=2160:-2,zoompan=z='1+0.0016*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=120:s=1080x1920:fps=30,"+",".join([cap("v3a1","CHARGE MAX :\n155 KG",0,1.9),cap("v3a2","TON APPLI :\n14 CHAMPS\nPOUR L'ÉCRIRE.",2.0,4.0)]),
 "-t","4","-c:v","libx264","-crf","21","-pix_fmt","yuv420p","seg/v3a.mp4"])
clip("seg/v3b.mp4",OV_COL,0.4,3.4,1.0,FIT,[cap("v3b","OVERBOLT :\nUN CHAMP.\nUN TAP.",0,3.4,y=170)])
endcard("seg/v3e.mp4",2.5,*END)
concat(["seg/v3a.mp4","seg/v3b.mp4","seg/v3e.mp4"],"V3_charge-max.mp4")
print("ok")
