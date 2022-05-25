%Computer Excercise 1.1.7

%the following program takes as input a 1D array of real numbers and
%evaluates the arithmetic mean, variance, and standard deviation of the
%array

function  prob7(a)
    n = length(a);
    %evaluate mean
    m = sum(a)/n ;
    
    %evaluate variance
    v = sum((a - m).^2)/(n-1);
   
    %evaluate standard deviation
    sigma = sqrt(v);  
    
    %display values
    fprintf('\n The arithmetic mean of the array is: %f \n The variance of the array is %f \n and the standard deviation of the array is %f \n', m, v, sigma)
end

