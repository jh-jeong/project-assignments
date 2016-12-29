def Tb(i,j,a1='',a2=''):
    while aT[i][j]!=0:cA=aT[i][j];a1,a2=('-',x[i])[cA%2]+a1,('-',y[j])[cA/2]+a2;i-=cA%2;j-=cA/2
    print a1;print a2
nC,tV,M=['A','C','G','T'],[],(0,0)
for i in xrange(4):tL=raw_input().split();tV.append(dict(zip(nC,map(int,tL))))
s=dict(zip(nC,tV));g,x,y=input()," "+raw_input()," "+raw_input();l1,l2=len(x),len(y);sT,aT=[[0]*l2 for i in xrange(l1)],[[0]*l2 for i in xrange(l1)]
for m,i,j in [(m,i,j)for m in [g,0]for i in range(l1)for j in range(l2)]: 
    if i*j==0:sT[i][j]=min(m*i,m*j);aT[i][j]=(0,int(bool(i))+2*int(bool(j)))[m!=0]
    else:cV=[(0,None)[m!=0],sT[i-1][j]+g,sT[i][j-1]+g,sT[i-1][j-1]+s[x[i]][y[j]]];sT[i][j]=max(cV);aT[i][j]=cV.index(sT[i][j]);M=(M,(i,j))[m!=0 or sT[i][j]>sT[M[0]][M[1]]]
    if i+j==l1+l2-2:print sT[M[0]][M[1]];Tb(M[0],M[1])