load btc_cn.txt
btc_future = btc_cn;
% 
% 
% tmp = btc_spot(:,2);
% tmp2 = btc_spot(:,5);
% 
% btc_future(:,2) = btc_future(:,2)./tmp;
% btc_future(:,3) = btc_future(:,3)./tmp;
% btc_future(:,4) = btc_future(:,4)./tmp;
% btc_future(:,5) = btc_future(:,5)./tmp2;

kline = btc_future(:,5);
high = btc_future(:,3);
low = btc_future(:,4);
kline_open = btc_future(:,2);
vol = btc_future(:,6);

kline = tmp;
kline_open = [tmp(1);tmp];
kline_open(end) = [];
high = max(kline_open,kline);
low = min(kline_open,kline);
vol = ones(size(tmp));

for i = 1:length(vol)
    %vol(i) = 1;
    if vol(i) == inf
        vol(i) = 0;
    end
end
%vol = ones(length(kline));
tl = 20;
lambda = 2;
max_stage = 4;
slip = 0;
p=1;

hedge_start = kline(tl);

X = -1:(2/(tl-1)):1;

BOLL_UPPER = zeros(1, tl);
BOLL_LOWER = zeros(1, tl);

%布林线是拟合的线性函数上下加减lambda倍的标准差


position = 0;
stage = 0;

buy_waiting = false;
sell_waiting = false;

asset_line = kline(1:tl);
cash = asset_line(end);

for i = tl+1:length(kline)
    hedge_profit = -kline(i) + hedge_start;
    asset = cash + position*kline_open(i); %+hedge_profit;
    asset_line = [asset_line; asset];
    % 拟合出来的函数坐标是从-1到1的
    para = PolySimu(kline(i-tl:i-1),vol(i-tl:i-1),p);
    
    % 计算标准差
    div = 0;
    for j = 1:tl
        div = div + vol(i-tl-1+j)*(kline(i-tl-1+j)-Poly(para, X(j)))^2;
    end
    div = div/sum(vol(i-tl:i-1));
    std = sqrt(div);
    
    BOLL_UPPER = [BOLL_UPPER, lambda*std+Poly(para, 1+2/(tl-1))];
    BOLL_LOWER = [BOLL_LOWER, -lambda*std+Poly(para, 1+2/(tl-1))];
    
    if high(i) > BOLL_UPPER(i) && low(i) < BOLL_LOWER(i)
        continue;
    end
    
    % 如果是在buy_waiting状态, 那么当价格进入BOLL_LOWER时, 就要买入了
    if buy_waiting && high(i)>BOLL_LOWER(i)
        price = max(kline_open(i),BOLL_LOWER(i));
        usecash = cash/(max_stage-stage);
        cash = cash - usecash;
        position = position + usecash/(price+slip);
        stage = stage+1;
        buy_waiting = false;
        fprintf('stage: %d, position: %f, cash: %f\n', stage, position, cash);
        continue;
    end
    
    % 如果是在sell_waiting状态, 那么当价格低于BOLL_UPPER时, 就要卖出了
    if sell_waiting && low(i)<BOLL_UPPER(i)
        price = min(kline_open(i), BOLL_UPPER(i));
        sellamt = position/stage;
        cash = cash + sellamt*(price-slip);
        position = position*(1-1/stage);
        stage = stage-1;
        sell_waiting = false;
        fprintf('stage: %d, position: %f, cash: %f\n', stage, position, cash);
        continue;
    end
    
    
    if low(i) < BOLL_LOWER(i)
        % 若仓位满了掉下了布林线下限, 就得清仓
%         if stage == max_stage
%             cash = cash+position*(BOLL_LOWER(i)-slip);
%             position = 0;
%             stage = 0;
%         end
        % 若仓位还不满
        if stage ~= max_stage
            % 若收盘时进入了BOLL_LOWER, 就已经买入了
            if kline(i) > BOLL_LOWER(i)
                usecash = cash/(max_stage-stage);
                cash = cash - usecash;
                position = position + usecash/(BOLL_LOWER(i)+slip);
                stage = stage+1;
                fprintf('stage: %d, position: %f, cash: %f\n', stage, position, cash);
            else
                buy_waiting = true;
            end
        end
    end
    
    if high(i) > BOLL_UPPER(i)
        % 若仓位不是0
        if stage ~= 0
            % 若收盘时进入了BOLL_UPPER, 就已经卖出了
            if kline(i) < BOLL_UPPER(i)
                %卖出的量是当前的1/stage
                sellamt = position/stage;
                cash = cash + sellamt*(BOLL_UPPER(i)-slip);
                position = position*(1-1/stage);
                stage = stage-1;
                fprintf('stage: %d, position: %f, cash: %f\n', stage, position, cash);
            else
                sell_waiting = true;
            end
        end
    end
end

N = 2000;

%DrawKLine(btc_future(end-N:end,:));
plot(kline(end-N:end))
hold on;
plot(BOLL_UPPER(end-N:end), 'red');
plot(BOLL_LOWER(end-N:end), 'red');
%BOLL_MEAN = (BOLL_UPPER+BOLL_LOWER)/2;
%plot(BOLL_MEAN(end-N:end), 'black');
plot(asset_line(end-N:end), 'yellow');