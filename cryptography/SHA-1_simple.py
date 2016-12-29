'''
Created on 2014. 10. 13.

@author: biscuit
'''
def sha1_simple(data):
    bytes = ""

    h0 = 0x86425897
    h1 = 0xACD89F45
    h2 = 0x125869DF
    h3 = 0x981274AE
    h4 = 0xCDFA58AE

    for n in range(len(data)):
        bytes+='{0:08b}'.format(ord(data[n]))
    bits = bytes+"1"
    pBits = bits
    #pad until length equals 448 mod 512
    while len(pBits)%512 != 448:
        pBits+="0"
    #append the original length
    pBits+='{0:064b}'.format(len(bits)-1)


    def chunks(l, n):
        return [l[i:i+n] for i in range(0, len(l), n)]


#    def rol(n, b):
#        return ((n << b) | (n >> (32 - b))) & 0xffffffff

    for c in chunks(pBits, 512): 
        words = chunks(c, 32)
        w = [0]*80
        for n in range(0, 16):
            w[n] = int(words[n], 2)
        for i in range(16, 80):
            w[i] = (w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16])

        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        

        #Main loop
        for i in range(0, 80):
            if 0 <= i <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x0
            elif 20 <= i <= 39:
                f = b ^ c ^ d
                k = 0x0
            elif 40 <= i <= 59:
                f = (b & c) | (b & d) | (c & d) 
                k = 0x0
            elif 60 <= i <= 79:
                f = b ^ c ^ d
                k = 0x0

            temp = a + f + e + k + w[i] & 0xffffffff
            e = d
            d = c
            c = b
            b = a
            a = temp
            

        h0 = h0 + a & 0xffffffff
        h1 = h1 + b & 0xffffffff
        h2 = h2 + c & 0xffffffff
        h3 = h3 + d & 0xffffffff
        h4 = h4 + e & 0xffffffff
    
    return '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)
        

print sha1_simple("Life is the art of drawing sufficient conclusions from insufficient premises.")
