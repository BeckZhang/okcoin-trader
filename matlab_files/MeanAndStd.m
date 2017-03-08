function [mean_x, std_x] = MeanAndStd(x, p)
p = p/sum(p);
sum_x = 0;

for i = 1:length(x)
    sum_x = sum_x+x(i)*p(i);
end

mean_x = sum_x;
div = 0;
for i = 1:length(x)
    div = div+p(i)*(x(i)-mean_x)^2;
end

std_x = sqrt(div);
