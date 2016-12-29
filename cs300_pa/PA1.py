'''
Created on 2014. 11. 19.

@author: biscuit
'''
def main():
    nChar, tVec = ['A', 'C', 'G', 'T'], []
    for i in xrange(4):
        tList = raw_input().split()
        tVec.append(dict(zip(nChar,map(int,tList))))
    score = dict(zip(nChar,tVec))
    gap, s1, s2 = int(raw_input()), " "+raw_input(), " "+raw_input()
    sT, aT = [[0]*len(s2) for i in xrange(len(s1))], [[0]*len(s2) for i in xrange(len(s1))]
    getAssignment(sT, aT, score, gap, s1, s2, 1), getAssignment(sT, aT, score, gap, s1, s2, 0)
    
def getAssignment(sT, aT, score, gap, s1, s2, m, M=(0,0)):
    for i, ai in enumerate(s1):
        for j, bj in enumerate(s2):
            if i*j == 0: sT[i][j] = min(m*gap*i, m*gap*j); aT[i][j] = (0,int(bool(i))+2*int(bool(j)))[m!=0]
            else:
                candVec = [(0,None)[m], sT[i-1][j]+gap, sT[i][j-1]+gap, sT[i-1][j-1]+score[ai][bj]]
                sT[i][j] = max(candVec); aT[i][j] = candVec.index(sT[i][j])
                M=(M,(i,j))[m!=0 or sT[i][j]>sT[M[0]][M[1]]]
    print sT[M[0]][M[1]]
    getTraceback(aT, s1, s2, M)
    
def getTraceback(aTable, s1, s2, (i,j), a1="", a2=""):
    while aTable[i][j] != 0:
        curArr = aTable[i][j]
        a1, a2 = ('-', s1[i])[curArr%2]+a1, ('-', s2[j])[curArr/2]+a2
        i -= curArr%2; j -= curArr/2
    print a1; print a2

if __name__ == '__main__':
    main()