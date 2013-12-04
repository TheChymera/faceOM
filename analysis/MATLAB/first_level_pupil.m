function first_level_pupil(type)
% 1st level batch for Trust Game, Trustee B, from Alena

%~clear all
%~close all
% List of subjects


list_faceOM;

%either simple, hdr, diff, or diff_hdr
%~type = 'simple' 

% loop over subjects in list
for s=1:length(list)
    
    subject = list{s};
 
    if strcmp(type,'simple') || strcmp(type,'hdr')
        numTR = 515;
    elseif strcmp(type,'diff') || strcmp(type,'diff_hdr')
        numTR = 515;
    end
        
    if strcmp(type,'simple')
        newFolder = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/results/pupil/'];
        movement_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/chr_rp_a' subject '_ep2d_faceOM.txt'];
        contrast_name = 'pupil+';
    elseif strcmp(type,'hdr')
        newFolder = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/results/pupil_hdr/'];
        movement_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/HDR_chr_rp_a' subject '_ep2d_faceOM.txt'];
        contrast_name = 'hdr_pupil+';
    elseif strcmp(type,'diff')
        newFolder = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/results/pupil_der/'];
        movement_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/diff_chr_rp_a' subject '_ep2d_faceOM.txt'];
        contrast_name = 'diff_pupil+';
    elseif strcmp(type,'diff_hdr')
        newFolder = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/results/pupil_der_hdr/'];
        movement_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/diff_HDR_chr_rp_a' subject '_ep2d_faceOM.txt'];
        contrast_name = 'diff_hdr_pupil+';
    end
    
    for i=1:numTR
        array_scan{i} =  ['/home/chymera/data/faceOM/fmri/first_level/' subject '/epi/faceOM/swa' subject '_ep2d_faceOM.nii,' num2str(i)]; 
    end
    %define onset file
    %~onset_file = ['/home/chymera/data/faceOM/fmri/first_level/' subject '/onsets/' subject '-faceOM_onset.mat'];
    %starts spm
    spm('defaults', 'FMRI');

    %-----------------------SPM Batch Job----------------------------------


matlabbatch{1}.spm.stats.fmri_spec.dir = {newFolder};
matlabbatch{1}.spm.stats.fmri_spec.timing.units = 'secs';
matlabbatch{1}.spm.stats.fmri_spec.timing.RT = 2;
matlabbatch{1}.spm.stats.fmri_spec.timing.fmri_t = 33;
matlabbatch{1}.spm.stats.fmri_spec.timing.fmri_t0 = 17;
%%
matlabbatch{1}.spm.stats.fmri_spec.sess.scans = array_scan;
%%
matlabbatch{1}.spm.stats.fmri_spec.sess.cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {});
matlabbatch{1}.spm.stats.fmri_spec.sess.multi = {''};
matlabbatch{1}.spm.stats.fmri_spec.sess.regress = struct('name', {}, 'val', {});
matlabbatch{1}.spm.stats.fmri_spec.sess.multi_reg = {movement_file};
matlabbatch{1}.spm.stats.fmri_spec.sess.hpf = 128;
matlabbatch{1}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});
matlabbatch{1}.spm.stats.fmri_spec.bases.hrf.derivs = [0 0];
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
matlabbatch{3}.spm.stats.con.spmmat(1).sname = 'Model estimation: SPM.mat File';
matlabbatch{3}.spm.stats.con.spmmat(1).src_exbranch = substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1});
matlabbatch{3}.spm.stats.con.spmmat(1).src_output = substruct('.','spmmat');

matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = contrast_name;
matlabbatch{3}.spm.stats.con.consess{1}.tcon.convec = [0 0 0 0 0 0 1];
matlabbatch{3}.spm.stats.con.consess{1}.tcon.sessrep = 'none';

matlabbatch{3}.spm.stats.con.delete = 0;


spm_jobman('run', matlabbatch)
end

