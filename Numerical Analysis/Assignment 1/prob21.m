% part a

x=0.1;
y=0.01;
z = x-y;
p = 1.0/3.0;
q = 3.0*p;
u = 7.6;
v = 2.9;
w = u - v;

%display using default format
fprintf('x = %f, y = %f, z = %f, p = %f, q = %f, u = %f, v = %f, w = %f \n',x,y,z,p,q,u,v,w)

%display using extremely large format field
fprintf('large format field:\n x = %30.20f,\n y = %30.20f,\n z = %30.20f,\n p = %30.20f,\n q = %30.20f,\n u = %30.20f, \n v = %30.20f,\n w = %30.20f \n',x,y,z,p,q,u,v,w)




%part b 
fprintf('\nValues computed: \n')
for n = 1:10
    x = (n-1)/2;
    y = (n^2)/3.0;
    z = 1.0 + 1/n;
    fprintf('x = %f, y = %f, z = %f \n',x,y,z)
end