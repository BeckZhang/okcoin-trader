function [diff, dea, bar] = MACD(close)
n = length(close);
diff = zeros(n,1);
dea = zeros(n,1);
ema12 = zeros(n,1);
ema26 = zeros(n,1);

ema12(1) = close(1);    ema26(1) = close(1);

for i = 2:n
    ema12(i) = ema12(i-1)*11/13.0 + close(i)*2/13.0;
    ema26(i) = ema26(i-1)*25/27.0 + close(i)*2/27.0;
    diff(i) = ema12(i)-ema26(i);
    dea(i) = dea(i-1)*0.8+diff(i)*0.2;
end

bar = 2*(diff-dea);