a, k, b, m, x = map(int, input().split())
L, R = 0, x * max(a, b)

while R - L > 1:
    M = (L + R) // 2
    if (M - M // k) * a + (M - M // m) * b >= x:
        R = M
    else:
        L = M
print(R)
