% %% sen slope analysis
% clc;clear;close all
% 
% filename='F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif';
% 
% [a,R]=geotiffread(filename);
% info=geotiffinfo(filename);
% [m,n]=size(a);
% % ��ʼ��ݣ��������
% start_year=2011;
% end_year=2021;
% 
% cd = end_year - start_year + 1;
% 
% datasum = zeros(m*n,cd) + NaN;
% 
% k=1;
% % ��ȡդ�����ݣ��洢��datasum������
% for year = start_year:end_year %��ʼ���
%     filename = ['F:\precipitation\spei12_trend_analysis\clip_spei12-',int2str(year),'-12.tif'];
%     data = importdata(filename);
%     data = reshape(data, m*n, 1);
%     datasum(:,k)=data;%���յ�datasum��һ������ݴ洢Ϊһ�У�����cd��
%     k=k+1;
% end
% result = zeros(m,n) + NaN;
% for i = 1:size(datasum,1)%datasum����ĵ�һά�ȣ���
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
%         result(i) = value;    %���д洢����m�к��Զ�����
%     end
% end
% % ����Sen������·��
% filename02 = 'F:\precipitation\spei12_trend_analysis\Sen1_2011_2021.tif';
% geotiffwrite(filename02,result,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);    
% 
% % MK analysis 
% 
% clc;clear;close all
% % ����ͶӰ��Ϣ
% [a,R]=geotiffread('F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif');
% info=geotiffinfo('F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif');
% [m,n]=size(a);
% % ʱ����
% years=2021-2011+1;
% datasum = zeros(m*n, years) + NaN; 
% p = 1;
% for year = 2011:2021      % ��ʼ���
%     filename = ['F:\precipitation\spei12_trend_analysis\clip_spei12-',int2str(year),'-12.tif'];;
%     data = importdata(filename);
%     data = reshape(data, m*n, 1);
%     datasum(:, p) = data; % datasum��m*n�У�years��
%     p = p + 1;
% end
% sresult = zeros(m, n) + NaN;% m��n�У�ֵȫΪNaN
% for i=1:m*n % size(datasum,1)��length(datasum)
%     data=datasum(i,:);% ��i�У�������
%     if min(data)>-4  % ��Ч����ж�����������Чֵ��0����
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
%                 sgnsum = [sgnsum;sgn];% data�ǰ�����ѭ�����㣬sgnsum�ǰ�����˳�δ洢���м�������洢Ϊ��
%             end
%         end  
%         add=sum(sgnsum);% ����ÿ�е����
%         sresult(i)=add; % ÿ�еĺ͸�ֵ��sresult����
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
% % ����MK������·��
% geotiffwrite('F:\precipitation\spei12_trend_analysis\MK2_2011_2021.tif',zc,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% %ע���޸�·��

%% դ������Sen's slope+Mk�����Լ���

clc;clear;close all
% ����ͶӰ��Ϣ
[a,R]=geotiffread('F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif');
info=geotiffinfo('F:\precipitation\spei12_trend_analysis\clip_spei12-1990-12.tif');

mkdata=importdata('F:\precipitation\spei12_trend_analysis\MK2_1990_2021.tif');
sen_value=importdata('F:\precipitation\spei12_trend_analysis\Sen1_1990_2021.tif');
sen_value(abs(mkdata)<1.96)=NaN;    % MK���ֵ����1.96����Ϊͨ����������95%
sen_value()
geotiffwrite('F:\precipitation\spei12_trend_analysis\sen_MK_2011_2021.tif',sen_value,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);

