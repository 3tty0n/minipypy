l = [1,2,3,4,5,6,7,8,9,10]

print l[1:]
print l[:1]
print l[1:2]

m = [1,2,3]

m[:] = [1]
print m

n = [1,2,3,4,5]
n[1:3] = [0]
print n

o = [1,2,3,4,5]
o[1:] = [0]
print o

p = [1,2,3,4,5]
p[:2] = [0]
print p
