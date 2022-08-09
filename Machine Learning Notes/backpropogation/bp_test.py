import numpy as np

#used reference: https://brilliant.org/wiki/backpropagation/

def sigmoid(x, derivative=False):

    if (derivative == True):
        return sigmoid(x,derivative=False) * (1 - sigmoid(x,derivative=False))
    else:
        return 1 / (1 + np.exp(-x))

X = np.array([  
    [0, 0, 1],
    [0, 1, 1],
    [1, 0, 0],
    [1, 1, 0],
    [1, 0, 1],
    [1, 1, 1],
    [0, 1, 0],
])

y = np.array([[0, 1, 0, 1, 1, 0, 1]]).T

alpha = 0.1

r0 = X.shape[1]
r1 = 3
r2 = 4
rm = 1

np.random.seed(1)
W1 = 2*np.random.random((r0 + 1, r1)) - 1
W2 = 2*np.random.random((r1 + 1, r2)) - 1
W3 = 2*np.random.random((r2 + 1, rm)) - 1

Y = y.copy()
iterations = 100000
m = 3
for i in range(iterations):
    O0 = np.hstack((np.ones((len(X), 1)), X))
    for k in np.arange(1,m):
        exec(f"A{k} = np.dot(O{k-1}, W{k})")
        exec(f"O{k}_star = sigmoid(A{k})")
        exec(f"O{k} = np.hstack((np.ones((len(O{k}_star),1)), O{k}_star))")
    exec(f"A{m} = np.dot(O{m-1}, W{m})")
    exec(f"Delta_{m} = A{m} - Y")
    for k in np.arange(m-1, 0, -1):
        exec(f"Delta_{k} = O{k}_star*(1 - O{k}_star)*(np.dot(Delta_{k+1}, W{k+1}[1:, :].T))")
    for k in np.arange(1,m+1):       
        exec(f"T1_O{k-1} = O{k-1}[:, :, np.newaxis]")
        exec(f"T2_Delta_{k} = Delta_{k}[:, np.newaxis, :]")
        exec(f"dE{k} = T1_O{k-1}*T2_Delta_{k}")
        exec(f"DE{k} = np.average(dE{k}, axis = 0)")
        exec(f"W{k} = W{k} - (alpha*DE{k})")
exec(f"out = A{m}")

print(out)
