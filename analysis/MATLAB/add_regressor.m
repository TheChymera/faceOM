function add_regressor(type)
% makes new movement file, incl. backward derivatives of movement, back-
% and forward derivatives of trigger not-equidistant pulses (triggered Fritz)
% may incl. WM, CSF and global signal regressors

%~clear all
%~close all

list = {
'ET001'
'ET002'
'ET003'
'ET004'
'ET005'
'ET006'
'ET007'
'ET008'
'ET009'
'ET010'
'ET011'
'ET012'
}

%either simple, hdr, diff, or diff_hdr
%~type = 'simple' 
%~type = type{1};

% loop over subjects in list
for s=1:length(list)
    
    subject = list{s}; %probandenliste
        
    movement_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/rp_a' subject '_ep2d_faceOM.txt'];
   
    if strcmp(type, 'simple')
        pupil =['/home/chymera/data/faceOM/eye_tracking/dfs/regressors/' subject '.csv'];
        new_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/chr_rp_a' subject '_ep2d_faceOM.txt'];
    elseif strcmp(type, 'hdr')
        pupil =['/home/chymera/data/faceOM/eye_tracking/dfs/regressors/' subject '.csv'];
        new_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/HDR_chr_rp_a' subject '_ep2d_faceOM.txt'];
    elseif strcmp(type, 'diff')
        pupil =['/home/chymera/data/faceOM/eye_tracking/dfs/regressors/' subject '_diff_prebin.csv'];
        new_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/diff_chr_rp_a' subject '_ep2d_faceOM.txt'];
    elseif strcmp(type, 'diff_hdr')
        pupil =['/home/chymera/data/faceOM/eye_tracking/dfs/regressors/' subject '_diff_prebin.csv'];
        new_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/diff_HDR_chr_rp_a' subject '_ep2d_faceOM.txt'];
    end

 %% movement regressors: 
    x=load(movement_file,'-ascii');
    y=load(pupil,'-ascii');
    if strcmp(type, 'simple') || strcmp(type,'hdr')
        z(1:515,1:6) = x(1:515,1:6);
    elseif strcmp(type,'diff') || strcmp(type,'diff_hdr')
        z(1:515,1:6) = x(1:515,1:6);
    end
    
%add regressor:
    if strcmp(type,'hdr') || strcmp(type,'diff_hdr')
        y = conv(y, spm_hrf(2));
    end
    
    if strcmp(type,'simple') || strcmp(type,'hdr')
        y = y(1:515); % HRF folding makes the vector longer, we crop it here.
        z(1:515,7) = y;
    elseif strcmp(type,'diff') || strcmp(type,'diff_hdr')
        y = y(1:515) % HRF folding makes the vector longer, we crop it here.
        z(1:515,7) = y;
    end

%% 
    save(new_file, 'z', '-ascii');
end
