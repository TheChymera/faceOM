% makes new movement file, incl. backward derivatives of movement, back-
% and forward derivatives of trigger not-equidistant pulses (triggered Fritz)
% may incl. WM, CSF and global signal regressors

clear all
close all

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

% loop over subjects in list
for s=1:length(list)
    
    subject = list{s}; %probandenliste
        
    movement_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/rp_a' subject '_ep2d_faceOM.txt'];
   
    newMovementFile = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/chr_rp_a' subject '_ep2d_faceOM.txt'];
    pupil =['/home/chymera/data/faceOM/eye_tracking/dfs/regressors/' subject '.csv'];

 %% movement regressors:   
    x=load(movement_file,'-ascii');
    y=load(pupil,'-ascii');
    z(1:515,1:6) = x(1:515,1:6);
    
%add regressor:    
    z(1:515,7)=y;
%% 
    save(newMovementFile, 'z', '-ascii');
end
