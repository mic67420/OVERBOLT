import math, random, struct, wave
random.seed(3); SR=44100; DUR=5.0; N=int(SR*DUR); mix=[0.0]*N
def add(t0,s,g=1.0):
    i0=int(t0*SR)
    for k,v in enumerate(s):
        j=i0+k
        if 0<=j<N: mix[j]+=v*g
T_ALARM,T_BOOM,T_LOGO=1.6,3.0,3.8
# ronronnement du réacteur + bips
for i in range(int(T_BOOM*SR)):
    t=i/SR; amp=0.10+0.10*min(1,t/T_BOOM)
    mix[i]+=amp*(math.sin(2*math.pi*55*t)+0.5*math.sin(2*math.pi*110*t+0.5))*0.6
t=0.2
while t<T_ALARM:
    add(t,[math.sin(2*math.pi*1320*k/SR)*math.exp(-k/SR*30)*0.35 for k in range(int(0.09*SR))]); t+=0.35
# sirène (balayage 600-950 Hz, ~1,3 Hz)
ph=0.0
for i in range(int(T_ALARM*SR),int(T_BOOM*SR)):
    t=i/SR-T_ALARM; tri=abs(((t*1.3)%1)*2-1)
    f=600+350*tri; ph+=2*math.pi*f/SR
    env=min(1,t/0.05)
    v=(math.sin(ph)+0.4*math.sin(2*ph)+0.2*math.sin(3*ph))*0.30*env
    mix[i]+=v
# explosion : coup sec + grondement + éclats + "cymbale"
def boom():
    L=int(1.3*SR);out=[];ph=0.0;lp=0.0
    for k in range(L):
        t=k/SR
        f=95*math.exp(-t*3.2)+28; ph+=2*math.pi*f/SR
        n=random.random()*2-1; lp+=0.08*(n-lp)
        v=math.sin(ph)*math.exp(-t*2.6)*1.0+lp*math.exp(-t*3.0)*1.6
        out.append(v)
    return out
def crash():
    L=int(1.1*SR);out=[];prev=0
    for k in range(L):
        n=random.random()*2-1;h=n-prev;prev=n
        out.append(h*math.exp(-k/SR*5.0)*0.5)
    return out
def pop():
    return [math.sin(2*math.pi*(900-3500*(k/SR))*k/SR)*math.exp(-k/SR*45)*0.7 for k in range(int(0.08*SR))]
add(T_BOOM,boom(),1.0);add(T_BOOM,crash(),0.6)
for tp,fq in [(0.35,880),(0.7,740),(1.0,990),(1.28,660),(1.5,1100)]:
    add(tp,[ (math.sin(2*math.pi*fq*k/SR)+0.4*math.sin(2*math.pi*fq*2*k/SR))*math.exp(-k/SR*14)*0.32 for k in range(int(0.22*SR))])
# whoosh + ding du logo
def whoosh():
    L=int(0.22*SR);out=[];lp=0.0
    for k in range(L):
        t=k/SR;n=random.random()*2-1;a=0.02+0.5*(t/0.22);lp+=a*(n-lp)
        out.append(lp*math.sin(math.pi*t/0.22)*0.8)
    return out
add(T_LOGO-0.05,whoosh(),0.6)
def ding():
    L=int(1.2*SR);out=[]
    for k in range(L):
        t=k/SR
        out.append((math.sin(2*math.pi*1318.5*t)+0.5*math.sin(2*math.pi*1975.5*t)+0.25*math.sin(2*math.pi*2637*t))*math.exp(-t*4.2)*0.35)
    return out
add(T_LOGO+0.08,ding(),1.0)
peak=max(abs(v) for v in mix) or 1; g=0.85/peak
data=bytearray()
for i,v in enumerate(mix):
    v*=g
    if i<int(0.02*SR): v*=i/(0.02*SR)
    data+=struct.pack('<h',int(max(-1,min(1,v))*32767))
w=wave.open('sfx.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(bytes(data));w.close()
