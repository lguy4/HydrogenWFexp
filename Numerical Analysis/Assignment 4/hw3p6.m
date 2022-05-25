digits(32);

pi32 = vpa(pi);

xvals = linspace(0, pi32/4);
tvals = linspace(0, pi/4);

yvals = p6(xvals);
uvals = p6(tvals);

function y=p6(x)
   y = sin(x) - 2.*((sin(x./2)).^2);
end