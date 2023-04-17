% %% sen slope analysis
% clc;clear;close all
% 
% filename='F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif';
% 
% [a,R]=geotiffread(filename);
% info=geotiffinfo(filename);
% [m,n]=size(a);
% % 开始年份，结束年份
% start_year=2011;
% end_year=2021;
% 
% cd = end_year - start_year + 1;
% 
% datasum = zeros(m*n,cd) + NaN;
% 
% k=1;
% % 读取栅格数据，存储至datasum矩阵中
% for year = start_year:end_year %起始年份
%     filename = ['F:\precipitation\spei12_trend_analysis\clip_spei12-',int2str(year),'-12.tif'];
%     data = importdata(filename);
%     data = reshape(data, m*n, 1);
%     datasum(:,k)=data;%最终的datasum是一年的数据存储为一列，共计cd列
%     k=k+1;
% end
% result = zeros(m,n) + NaN;
% for i = 1:size(datasum,1)%datasum矩阵的第一维度：列
%     data = datasum(i,:);
%     if min(data) > -4 
%         valuesum = [];
%         for k1=2:cd
%             for k2=1:(k1-1)
%                 cz = data(k1)-data(k2);
%                 jl = k1-k2;
%                 value = cz./jl;
%                 valuesum = [valuesum;value];
%             end
%         end
%         value = median(valuesum);
%         result(i) = value;    %按列存储，至m行后自动换列
%     end
% end
% % 保存Sen计算结果路径
% filename02 = 'F:\precipitation\spei12_trend_analysis\Sen1_2011_2021.tif';
% geotiffwrite(filename02,result,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);    
% 
% % MK analysis 
% 
% clc;clear;close all
% % 导入投影信息
% [a,R]=geotiffread('F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif');
% info=geotiffinfo('F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif');
% [m,n]=size(a);
% % 时间跨度
% years=2021-2011+1;
% datasum = zeros(m*n, years) + NaN; 
% p = 1;
% for year = 2011:2021      % 起始年份
%     filename = ['F:\precipitation\spei12_trend_analysis\clip_spei12-',int2str(year),'-12.tif'];;
%     data = importdata(filename);
%     data = reshape(data, m*n, 1);
%     datasum(:, p) = data; % datasum是m*n行，years列
%     p = p + 1;
% end
% sresult = zeros(m, n) + NaN;% m行n列，值全为NaN
% for i=1:m*n % size(datasum,1)或length(datasum)
%     data=datasum(i,:);% 第i行，所有列
%     if min(data)>-4  % 有效格点判定，我这里有效值在0以上
%         sgnsum=[];  
%         for k=2:years
%             for j=1:(k-1)
%                 sgn=data(k)-data(j);
%                 if sgn>0
%                     sgn=1;
%                 else
%                     if sgn<0
%                         sgn=-1;
%                     else
%                         sgn=0;
%                     end
%                 end
%                 sgnsum = [sgnsum;sgn];% data是按照行循环计算，sgnsum是按照列顺次存储，行计算后结果存储为列
%             end
%         end  
%         add=sum(sgnsum);% 计算每列的求和
%         sresult(i)=add; % 每列的和赋值给sresult矩阵
%     end
% end
% vars=p * (p - 1) * (2 * p + 5) / 18;
% zc=zeros(m,n)+NaN;
% sy=find(sresult==0);
% zc(sy)=0;
% sy=find(sresult>0);
% zc(sy)=(sresult(sy)-1)./sqrt(vars);
% sy=find(sresult<0);
% zc(sy)=(sresult(sy)+1)./sqrt(vars);
% % 保存MK计算结果路径
% geotiffwrite('F:\precipitation\spei12_trend_analysis\MK2_2011_2021.tif',zc,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% %注意修改路径

%% 栅格数据Sen's slope+Mk显著性检验

clc;clear;close all
% 导入投影信息
[a,R]=geotiffread('F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif');
info=geotiffinfo('F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif');

mkdata=importdata('F:\precipitation\spei12_trend_analysis\MK2_1990_2021.tif');
sen_value=importdata('F:\precipitation\spei12_trend_analysis\Sen1_1990_2021.tif');
sen_value(abs(mkdata)<1.96)=NaN;    % MK结果值高于1.96则认为通过了显著性95%
sen_value()
geotiffwrite('F:\precipitation\spei12_trend_analysis\sen_MK_2011_2021.tif',sen_value,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);

