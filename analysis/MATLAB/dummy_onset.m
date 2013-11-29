function dummy_onset(ID_list)
%
% Usage: calculate_onsets({'firstID','secondID','otherID'})
%

outfile = strcat('/home/chymera/data/faceOM/fmri/onsets/dummy.mat'); %general expression for your output. Make sure the directories are created

durations={[130]}; % 4S, 2 tr DURATION FOR TASKS
onsets={[0]};
names={'dummy'};

save(outfile,'names','onsets','durations');
end
