function sum = simpson_comp(f, a, b, n)
    %check for even n
    if mod(n,2) == 0
        N = n;
    else
        N = n + 1;
    end
    h = (b - a)/N;
    sum = (f(a) + f(b))*(h/3);
    for i = 1:((N-2)/2)
        sum = sum + ((2*h)/3)*f(a + 2*i*h);
    end
    for j = 1:(n/2)
        sum = sum + ((4*h)/3)*f(a + ((2*j)-1)*h);
    end
end