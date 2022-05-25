function result = simpson_recur(f, a, b, err, level, max_level)
    level = level + 1;
    h = b - a;
    c = (a + b)/2;
    simpson_1 = (h/6)*(f(a) + 4*f(c) + f(b));
    d = (a + c)/2;
    e = (c + b)/2;
    simpson_2 = (h/12)*(f(a)+ 4*f(d) + 2*f(c) + 4*f(e) + f(b));
    if level >= max_level
        result = simpson_2;
        %fprintf('max level reached: level = %d, result = %12.12f, a = %12.12f, b = %12.12f \n', level, result, a, b)
    else
        if abs(simpson_1 - simpson_2) < 15*err
            result = simpson_2 + (simpson_2 - simpson_1)/15;
            %fprintf('error tolerance satisfied: level = %d, result = %12.12f, a = %12.12f, b = %12.12f \n', level, result, a, b)
        else
            left_simpson = simpson_recur(f, a, c, err/2, level, max_level);
            right_simpson = simpson_recur(f, c, b, err/2, level, max_level);
            result = left_simpson + right_simpson;
            %fprintf('level = %d, result = %12.12f, a = %12.12f, b = %12.12f \n', level, result, a, b)
        end        
    end 
end