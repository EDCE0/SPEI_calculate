clc;
clear all;
location = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\normal_data\';
SPEIFile = dir([location,'*spei3*','.tif']);
fileNumber = length(SPEIFile);

SSMIFile = dir([location,'*SSMI*','.tif']);

GPPFile = dir([location,'*GPP*','.tif']);

REFile = dir([location,'*Re*','.tif']);

SSMI_data = zeros(101*125,fileNumber)
SPEI_data = zeros(101*125,fileNumber)
GPP_data = zeros(101*125,fileNumber)
RE_data = zeros(101*125,fileNumber)
for i=1:fileNumber
    path = [location,SPEIFile(i).name]
    data=importdata(path);
    data = data(1:101,:);
    data=reshape(data,101*125,1);
    SPEI_data(:,i) = data;
        
    path2 = [location,SSMIFile(i).name]
    data2=importdata(path2);
    data2 = data2(1:101,:);
    data2=reshape(data2,101*125,1);
    SSMI_data(:,i) = data2;
        
    path3 = [location,GPPFile(i).name]
    data3=importdata(path3);
    data3 = data3(1:101,:);
    data3=reshape(data3,101*125,1);
    GPP_data(:,i) = data3;
        
    path4 = [location,REFile(i).name]
    data4=importdata(path4);
    data4 = data4(1:101,:);
    data4=reshape(data4,101*125,1);
    RE_data(:,i) = data4;    
end

regression_coe_spei_gpp = zeros(101*125)+NaN;
regression_coe_ssmi_gpp = zeros(101*125)+NaN;

regression_p_spei_gpp = zeros(101*125)+NaN;
regression_p_ssmi_gpp = zeros(101*125)+NaN;
R2_gpp = zeros(101*125)+NaN;


regression_coe_spei_re = zeros(101*125)+NaN;
regression_coe_ssmi_re = zeros(101*125)+NaN;

regression_p_spei_re = zeros(101*125)+NaN;
regression_p_ssmi_re = zeros(101*125)+NaN;
R2_re = zeros(101*125)+NaN;

for i=1:101*125
    spei_xy = SPEI_data(i,:)';
    if min(spei_xy>-5)
        ssmi_xy = SSMI_data(i,:)';
        X = [spei_xy,ssmi_xy];
        gpp_xy = GPP_data(i,:)';
        mdl = fitlm(X, gpp_xy);
        disp(mdl);
%         regression_coe_spei_gpp(i) = mdl.Coefficients.Estimate(2);
%         regression_coe_ssmi_gpp(i) = mdl.Coefficients.Estimate(3);
%         regression_p_spei_gpp(i) = mdl.Coefficients.pValue(2);
%         regression_p_ssmi_gpp(i) = mdl.Coefficients.pValue(3);
%         R2_gpp(i) = mdl.Rsquared.Ordinary;
        
        
%         re_xy = RE_data(i,:)';
%         
%         mdl2 = fitlm(X, re_xy);
%         regression_coe_spei_re(i) = mdl2.Coefficients.Estimate(2);
%         regression_coe_ssmi_re(i) = mdl2.Coefficients.Estimate(3);
%         regression_p_spei_re(i) = mdl2.Coefficients.pValue(2);
%         regression_p_ssmi_re(i) = mdl2.Coefficients.pValue(3);
%         R2_re(i) = mdl2.Rsquared.Ordinary;     
    end
end
% [a,R]=geotiffread('F:\precipitation\3.4SPEISSMIGPPRE\contribution\normal_data\nor_resample_SA_clip_spei3_2009_8.tif');%先导入投影信息
% info=geotiffinfo('F:\precipitation\3.4SPEISSMIGPPRE\contribution\normal_data\nor_resample_SA_clip_spei3_2009_8.tif');
% 
% filename1 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\regression_coe_spei_gpp.tif';
% filename2 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\regression_coe_ssmi_gpp.tif';
% filename3 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\regression_p_spei_gpp.tif';
% filename4 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\regression_p_ssmi_gpp.tif';
% filename5 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\R2_gpp.tif';
% 
% filename6 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\regression_coe_spei_re.tif';
% filename7 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\regression_coe_ssmi_re.tif';
% filename8 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\regression_p_spei_re.tif';
% filename9 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\regression_p_ssmi_re.tif';
% filename10 = 'F:\precipitation\3.4SPEISSMIGPPRE\contribution\R2_re.tif';
% 
% 
% geotiffwrite(filename1,reshape(regression_coe_spei_gpp(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename2,reshape(regression_coe_ssmi_gpp(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename3,reshape(regression_p_spei_gpp(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename4,reshape(regression_p_ssmi_gpp(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename5,reshape(R2_gpp(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename6,reshape(regression_coe_spei_re(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename7,reshape(regression_coe_ssmi_re(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename8,reshape(regression_p_spei_re(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename9,reshape(regression_p_ssmi_re(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);
% geotiffwrite(filename10,reshape(R2_re(:,1),[101 125]),R,'GeoKeyDirectoryTag',info.GeoTIFFTags.GeoKeyDirectoryTag);


