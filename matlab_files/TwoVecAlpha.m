function f = TwoVecAlpha(x,y)
% 这个函数在给出两个数列x和y的情况下, 
% 求出最合适的a, 使得
% \sigma (xi-a*yi)^2 = min
% 即 min (x-a*y)'*(x-a*y) = min
% 拆开有, x'*x - 2*a*x'*y + a^2*y'*y
% 所以 a = x'*y/(y'*y)

f = (x'*y)/(y'*y);