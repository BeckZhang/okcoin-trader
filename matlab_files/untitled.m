load diff.txt
load dea.txt
load bar.txt
plot(diff(end-200:end));
hold on;
plot(dea(end-200:end), 'yellow');
plot(bar(end-200:end), 'red');
plot(zeros(201,1), 'black');

load kclose.txt
[diff, dea, bar] = MACD(kclose);
plot(diff(end-200:end));
hold on;
plot(dea(end-200:end), 'yellow');
plot(bar(end-200:end), 'red');
plot(zeros(201,1), 'black');
