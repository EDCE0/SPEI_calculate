clc;
clear all;
location = 'F:\precipitation\gpp_val_Data\cor_gpp\gpp_sim\';
SMFile = dir([location,'*.tif']);
fileNumber = length(SMFile);
CoLM_SM_sum=zeros(101*125,72);
for i=1:fileNumber
    path = [location,SMFile(i).name]
    data=importdata(path);
    data = data(1:101,:);
    data = data *12*86400*30; 
    data=reshape(data,101*125,1);
    CoLM_SM_sum(:,i) = data;
end

location2 = 'F:\precipitation\gpp_val_Data\cor_gpp\gpp_val\';
SMFile2 = dir([location2,'*.tif']);
fileNumber2 = length(SMFile2);
FLDAS_SM_sum=zeros(101*125,72);
for i=1:fileNumber2
    path = [location2,SMFile2(i).name]
    data=importdata(path);
    data=data*0.1; %gc month
    data=reshape(data,101*125,1);
    FLDAS_SM_sum(:,i) = data;
end

Colm_FLDAS_xgx =zeros(101,125);

Colm_FLDAS_p = zeros(101,125);
for i=1:length(CoLM_SM_sum)
    CoLM=CoLM_SM_sum(i,:);
    if min(CoLM)>0 %ע�������NPP����Ч��Χ�Ǵ���0������Լ���������Ч��Χ��С��0�Ļ�������Բ��ü����
        FLDAS=FLDAS_SM_sum(i,:);
         [r2,p2]=corrcoef(CoLM,FLDAS);
         Colm_FLDAS_xgx(i)=r2(2);
         Colm_FLDAS_p(i)=p2(2);
    end
end
Colm_FLDAS_p(Colm_FLDAS_p>0.05)=nan;
filename5='F:\precipitation\gpp_val_Data\cor_gpp\CoLM_gpp_correlation.tif';
filename6='F:\precipitation\gpp_val_Data\cor_gpp\CoLM_gpp_p_2.tif';
[a,R]=geotiffread('F:\precipitation\gpp_val_Data\cor_gpp\gpp_val\resample_clip_GPP_v21_2005_07.tif');%�ȵ���ͶӰ��Ϣ
info=geotiffinfo('F:\precipitation\gpp_val_Data\cor_gpp\gpp_val\resample_clip_GPP_v21_2005_07.tif');
%%���ͼ��
geotiffwrite(filename5,Colm_FLDAS_xgx,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
geotiffwrite(filename6,Colm_FLDAS_p,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);


% %�����߶�������ݷ���������ͬ�ľ�����
% nppsum=zeros(3587*4642,72);
% month = [01,02,03,04,05,06,07,08,09,10,11,12];
% i=1;
% for year=2000:2015
%     filename=strcat('F:\precipitation\FLADS_VAL_data\Colm_soil_moisture\clip_SMroot-10cm-',int2str(year),'npp.tif');
%     data=importdata(filename);
%     data=reshape(data,3587*4642,1);
%     nppsum(:,year-1999)=data;
% end
% ?
% wcsum=zeros(3587*4642,16);
% for year=2000:2015
%     filename=strcat('F:\������Ŀ\data\',int2str(year),'water_yield.tif');
%     data=importdata(filename);
%     data=reshape(data,3587*4642,1);
%     wcsum(:,year-1999)=data;
% end
% %����Ժ�������
% npp_wc_xgx=zeros(3587,4642);
% npp_wc_p=zeros(3587,4642);
% for i=1:length(nppsum)
%     npp=nppsum(i,:);
%     if min(npp)>0 %ע�������NPP����Ч��Χ�Ǵ���0������Լ���������Ч��Χ��С��0�Ļ�������Բ��ü����
%         wc=wcsum(i,:);
%          [r2,p2]=corrcoef(npp,wc);
%          npp_wc_xgx(i)=r2(2);
%          npp_wc_p(i)=p2(2);
%     end
% end
% filename5='F:\result\npp_wc�����.tif';
% filename6='F:\npp_wc������.tif';
% ?
% [a,R]=geotiffread('F:\��Ŀ\data\2002water_yield.tif');%�ȵ���ͶӰ��Ϣ
% info=geotiffinfo('F:\��Ŀ\data\2002water_yield.tif');
% %%���ͼ��
% geotiffwrite(filename5,npp_wc_xgx,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename6,npp_wc_p,R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);