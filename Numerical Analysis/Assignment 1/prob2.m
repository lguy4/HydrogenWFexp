%Computer Excercise 1.1.2

%mostly the same as 1.1.1

%The following program will evaluate the finite difference quotient of
%f(x) = 1/(1 + x^2) for different values of h as an approximation for the first
%derivative of f(x); the program will loop through different values of h
%multiplying the previous value of h by 0.25 on each iteration

%The program will then evaluate the error of the approximation by using
%f(x)'s known derivative, f'(x) = -(2*x)/((1 + x^2)^2), and will seek out and store 
%a smallest error value and its corresponding index 

%On each iteration, desired values will be stored in an array which will
%then be casted as a table for display.

%Initialize values

n=30;
x=0.5;
h = 1;
emin = 1;

%Initialize output arrays which will then be used to display a table
%This portion is for display purposes

i_out = (1:30)';
h_out = zeros(30,1);
y_out = zeros(30,1);
error_out = zeros(30,1);

%approximation program loop for f(x)

%function and derivative are written at the bottom of the script

for i = 1:n
    h = 0.25*h;
    y = (f(x + h) - f(x))/h;
    error = abs( deriv(x) - y );
    
    %update the output arrays
    h_out(i) = h;
    y_out(i) = y;
    error_out(i) = error; 
   
    %seek out minimum error and record its index
    if error < emin
        emin = error;
        imin = i;
    end  
end

%cast output arrays as a table

T = table(i_out, h_out, y_out, error_out)

%display the minimum error and its index

fprintf('\n The minimum error occurs at i = %d has a value of %d \n', imin, emin)

%This function and its derivative are a bit chunky so I'm going to write them here to make
%things neater

function y=f(x)
    y = 1/(1 + x^2);
end

function y=deriv(x)
    y = -(2*x)/((1 + x^2)^2);
end

