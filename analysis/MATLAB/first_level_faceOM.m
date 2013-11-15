% 1st level batch for Trust Game, Trustee B, from Alena

clear all
close all
% List of subjects


list_faceOM;


% loop over subjects in list
for s=1:length(list)
    
    subject = list{s};
    newFolder = ['/home/klips/Documents/Eye_Tracking/first_level/' subject '/results/faceOM/'];
 
    
    for i=1:520 
        array_scan{i} =  ['/home/klips/Documents/Eye_Tracking/first_level/' subject '/epi/faceOM/swa' subject '_ep2d_faceOM.nii,' num2str(i)]; 
    end
    %define onset file
    onset_file = ['/home/klips/Documents/Eye_Tracking/first_level/' subject '/onsets/' subject '-faceOM_onset.mat'];
    %define movement regressor file
    movement_file = ['/home/klips/Documents/Eye_Tracking/first_level/' subject '/epi/faceOM/rp_a' subject '_ep2d_faceOM.txt'];
    %starts spm
    spm('defaults', 'FMRI');

    %-----------------------SPM Batch Job----------------------------------
    
 %-----------------------------------------------------------------------
% Job configuration created by cfg_util (rev $Rev: 3944 $)
%-----------------------------------------------------------------------
matlabbatch{1}.spm.stats.fmri_spec.dir = {newFolder};
matlabbatch{1}.spm.stats.fmri_spec.timing.units = 'scans';
matlabbatch{1}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{1}.spm.stats.fmri_spec.timing.fmri_t = 33;
matlabbatch{1}.spm.stats.fmri_spec.timing.fmri_t0 = 17;
%%
matlabbatch{1}.spm.stats.fmri_spec.sess.scans = array_scan;
%%
matlabbatch{1}.spm.stats.fmri_spec.sess.cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {});
matlabbatch{1}.spm.stats.fmri_spec.sess.multi = {onset_file};
matlabbatch{1}.spm.stats.fmri_spec.sess.regress = struct('name', {}, 'val', {});
matlabbatch{1}.spm.stats.fmri_spec.sess.multi_reg = {movement_file};
matlabbatch{1}.spm.stats.fmri_spec.sess.hpf = 128;
matlabbatch{1}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{1}.spm.stats.fmri_spec.bases.hrf.derivs = [1 1];
matlabbatch{1}.spm.stats.fmri_spec.volt = 1;
matlabbatch{1}.spm.stats.fmri_spec.global = 'None';
matlabbatch{1}.spm.stats.fmri_spec.mask = {''};
matlabbatch{1}.spm.stats.fmri_spec.cvi = 'AR(1)';
matlabbatch{2}.spm.stats.fmri_est.spmmat(1) = cfg_dep;
matlabbatch{2}.spm.stats.fmri_est.spmmat(1).tname = 'Select SPM.mat';
matlabbatch{2}.spm.stats.fmri_est.spmmat(1).tgt_spec{1}(1).name = 'filter';
matlabbatch{2}.spm.stats.fmri_est.spmmat(1).tgt_spec{1}(1).value = 'mat';
matlabbatch{2}.spm.stats.fmri_est.spmmat(1).tgt_spec{1}(2).name = 'strtype';
matlabbatch{2}.spm.stats.fmri_est.spmmat(1).tgt_spec{1}(2).value = 'e';
matlabbatch{2}.spm.stats.fmri_est.spmmat(1).sname = 'fMRI model specification: SPM.mat File';
matlabbatch{2}.spm.stats.fmri_est.spmmat(1).src_exbranch = substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1});
matlabbatch{2}.spm.stats.fmri_est.spmmat(1).src_output = substruct('.','spmmat');
matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;
matlabbatch{3}.spm.stats.con.spmmat(1) = cfg_dep;
matlabbatch{3}.spm.stats.con.spmmat(1).tname = 'Select SPM.mat';
matlabbatch{3}.spm.stats.con.spmmat(1).tgt_spec{1}(1).name = 'filter';
matlabbatch{3}.spm.stats.con.spmmat(1).tgt_spec{1}(1).value = 'mat';
matlabbatch{3}.spm.stats.con.spmmat(1).tgt_spec{1}(2).name = 'strtype';
matlabbatch{3}.spm.stats.con.spmmat(1).tgt_spec{1}(2).value = 'e';
matlabbatch{3}.spm.stats.con.spmmat(1).sname = 'fMRI model specification: SPM.mat File';
matlabbatch{3}.spm.stats.con.spmmat(1).src_exbranch = substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1});
matlabbatch{3}.spm.stats.con.spmmat(1).src_output = substruct('.','spmmat');
matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = 'em100_HA > cell22';
matlabbatch{3}.spm.stats.con.consess{1}.tcon.convec = [1/3 1/3 1/3 0 0 0 0 0 0 0 0 0 -1/3 -1/3 -1/3];
matlabbatch{3}.spm.stats.con.consess{1}.tcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.consess{2}.tcon.name = 'em100_FE > cell22';
matlabbatch{3}.spm.stats.con.consess{2}.tcon.convec = [0 0 0  1/3 1/3 1/3 0 0 0 0 0 0 -1/3 -1/3 -1/3];
matlabbatch{3}.spm.stats.con.consess{2}.tcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.consess{3}.tcon.name = 'em40_HA > cell10';
matlabbatch{3}.spm.stats.con.consess{3}.tcon.convec = [0 0 0 0 0 0  1/3 1/3 1/3 0 0 0 0 0 0 -1/3 -1/3 -1/3];
matlabbatch{3}.spm.stats.con.consess{3}.tcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.consess{4}.tcon.name = 'em40_FE > cell10';
matlabbatch{3}.spm.stats.con.consess{4}.tcon.convec = [0 0 0 0 0 0 0 0 0 1/3 1/3 1/3  0 0 0 -1/3 -1/3 -1/3];
matlabbatch{3}.spm.stats.con.consess{4}.tcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.consess{5}.tcon.name = 'cell22 > cell10';
matlabbatch{3}.spm.stats.con.consess{5}.tcon.convec = [0 0 0 0 0 0 0 0 0 0 0 0  1/3 1/3 1/3  -1/3 -1/3 -1/3];
matlabbatch{3}.spm.stats.con.consess{5}.tcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.consess{6}.fcon.name = 'alles';
matlabbatch{3}.spm.stats.con.consess{6}.fcon.convec = {
                                                       eye(24)
                                                       }';
matlabbatch{3}.spm.stats.con.consess{6}.fcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.delete = 0;


    %-----------------------SPM Batch Job END------------------------------
    
    %runs matlab batch
    spm_jobman('run', matlabbatch)


end