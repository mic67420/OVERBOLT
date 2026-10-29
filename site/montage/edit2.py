import subprocess, os, sys
V="/root/.claude/uploads/4c8d8528-44e8-5d64-a3bd-288f4cee0e4d/5026c61a-Screenrecorder-2026-10-07-19-38-59-339.mp4"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def cap_file(name,text):
    p=f"cap/{name}.txt"; open(p,"w",encoding="utf-8").write(text); return p
def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
def segment(out,start,dur_src,speed,caps):
    out_dur=dur_src/speed
    # recadre l'app (retire barre d'état et barre de navigation Android), recentre sur 720x1280
    vf=[f"setpts=PTS/{speed}","fps=30","crop=720:1150:0:60","pad=720:1280:0:65:color=0x05070a"]
    for i,(txt,t0,t1) in enumerate(caps):
        f=cap_file(f"{os.path.basename(out)}_{i}",txt)
        vf.append(f"drawtext=fontfile={FONT}:textfile={f}:fontsize=34:fontcolor=white:borderw=2:bordercolor=black:text_align=center:x=(w-text_w)/2:y=h*0.68:box=1:boxcolor=black@0.66:boxborderw=20:enable='between(t,{t0},{t1})'")
    run(["ffmpeg","-v","error","-y","-ss",str(start),"-t",str(dur_src),"-i",V,"-an","-vf",",".join(vf),"-t",f"{out_dur:.3f}","-c:v","libx264","-preset","medium","-crf","24","-pix_fmt","yuv420p",out])
def endcard(out,dur,lines):
    f1=cap_file("end_title",lines[0]); f2=cap_file("end_sub",lines[1]); f3=cap_file("end_cta",lines[2])
    vf=(f"drawtext=fontfile={FONT}:textfile={f1}:fontsize=58:fontcolor=white:x=(w-text_w)/2:y=330,"
        f"drawtext=fontfile={FONT}:textfile={f2}:fontsize=44:fontcolor=0x2af5e0:text_align=center:x=(w-text_w)/2:y=520,"
        f"drawtext=fontfile={FONT}:textfile={f3}:fontsize=36:fontcolor=0x9aa7b4:text_align=center:x=(w-text_w)/2:y=860")
    run(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=0x05070a:s=720x1280:r=30:d={dur}","-vf",vf,"-c:v","libx264","-crf","24","-pix_fmt","yuv420p",out])
def concat(parts,out):
    open("list.txt","w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","list.txt","-c:v","libx264","-preset","medium","-crf","25","-pix_fmt","yuv420p","-movflags","+faststart","-an",out])
END=["OVERBOLT | NO BS","5 € une seule fois.\nPas d'abonnement.\nPas une centrale nucléaire.","Aucun compte. Aucune inscription."]
# ---------- VERSION SITE (~40 s) ----------
site=[]
segment("seg/s1.mp4",0.0,10.0,1.25,[("Ton appli de muscu :\nle cockpit d'un A380.",0.2,3.4),("Overbolt : tu poses la charge,\ntu coches. Fin du briefing.",3.8,7.8)]); site.append("seg/s1.mp4")
segment("seg/s2.mp4",3.5,6.0,1.4,[("La photo du réglage machine.\nParce que \"siège cran 6\",\nça s'oublie.",0.2,4.1)]); site.append("seg/s2.mp4")
segment("seg/s3.mp4",10.0,15.0,2.0,[("Chrono de repos automatique.\nTu respires, il compte.",0.2,7.2)]); site.append("seg/s3.mp4")
segment("seg/s4.mp4",30.0,12.0,1.6,[("Série terminée ? Un tap.\nZéro comité de pilotage.",0.2,7.3)]); site.append("seg/s4.mp4")
segment("seg/s5.mp4",43.0,10.0,1.6,[("Le bilan : ce que t'as soulevé.\nPas un rapport de sûreté\nnucléaire.",0.3,6.0)]); site.append("seg/s5.mp4")
segment("seg/s6.mp4",53.5,11.0,2.2,[("Les réglages : une page.\nPas de salle de contrôle.",0.1,4.9)]); site.append("seg/s6.mp4")
endcard("seg/end.mp4",3.5,END); site.append("seg/end.mp4")
concat(site,"demo_site.mp4")
# ---------- VERSION RÉSEAUX (~17 s) ----------
soc=[]
segment("seg/r1.mp4",0.0,6.0,1.5,[("Ton appli de muscu actuelle :\nun réacteur nucléaire ?",0.1,1.9),("Overbolt : je pose la charge,\nje coche. C'est tout.",2.0,3.9)]); soc.append("seg/r1.mp4")
segment("seg/r2.mp4",30.0,12.0,3.0,[("Série terminée ? Un tap.\nZéro réunion.",0.1,3.9)]); soc.append("seg/r2.mp4")
segment("seg/r3.mp4",44.0,8.0,2.0,[("Un bilan. Pas un rapport\nde sûreté nucléaire.",0.1,3.9)]); soc.append("seg/r3.mp4")
endcard("seg/end2.mp4",3.0,END); soc.append("seg/end2.mp4")
concat(soc,"demo_court.mp4")
print("ok")
