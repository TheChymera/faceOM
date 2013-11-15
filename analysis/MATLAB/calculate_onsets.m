function calculate_onsets(ID_list)
%
% Usage: calculate_onsets({'firstID','secondID','otherID'})
%
for ID = ID_list
    logfile=strcat('/home/chymera/data/faceOM/fmri/logfiles/faceOM/',ID,'-faceOM.log'); %general expression for input (so-called log) files.
    outfile = strcat('/home/chymera/data/faceOM/fmri/',ID,'/onsets/',ID,'-faceOM_onset.mat'); %general expression for your output. Make sure the directories are created
    
    TR=2; %full volume acquisition time in seconds
    
    display(logfile{1}) %keeps track of progress
    
    %BEGIN DETERMNING THE LENGTH OF THE TIME SERIES IN THE LOG FILE (MEASURED IN LINES)
    [lines, rest2, rest3, rest4, rest5, rest6, rest7, rest8, rest9, rest0, resta, rests, rest1]=textread(logfile{1},'%s %s %s %s %s %s %s %s %s %s %s %s %s','headerlines',5);
    
    for i=1:length(lines)
        if strcmp(lines{i},'Event')
            time_series_length = i-3;
        end;    
    end;    
    %END DETERMNING THE LENGTH OF THE TIME SERIES IN THE LOG FILE (MEASURED IN LINES)

    onset_em100_HA=[];
    onset_em100_FE=[];
    onset_em40_HA=[];
    onset_em40_FE=[];
    onset_cell22=[];
    onset_cell10=[];
    
    
    [Subject,Trial,Event_Type,Code,Time,TTime,Uncertainty,Duration,Uncertainty2,ReqTime,ReqDur,Stim_Type,Pair_Index]=textread(logfile{1},'%s %n %s %s %s %n %s %s %s %s %s %s %s',time_series_length,'headerlines',5);
    
    pulse_count = 0;
    
    for i = 1:length(Trial)
        if strcmp(Event_Type{i},'Pulse')
            pulse_count=pulse_count+1;
            if pulse_count == 4
                start_time=str2num(Time{i})
            end;
        end;
    end;   
    
    for i = 1:time_series_length
        if strfind(Code{i},'em100') & strfind(Code{i},'HA')
            onset_em100_HA=[onset_em100_HA,str2num(Time{i})];
        end
        if strfind(Code{i},'em100') & strfind(Code{i},'FE')
            onset_em100_FE=[onset_em100_FE,str2num(Time{i})];
        end
        if strfind(Code{i},'em40') & strfind(Code{i},'HA')
            onset_em40_HA=[onset_em40_HA,str2num(Time{i})];
        end
        if strfind(Code{i},'em40') & strfind(Code{i},'FE')
            onset_em40_FE=[onset_em40_FE,str2num(Time{i})];
        end
        if strfind(Code{i},'cell22')
            display(Time{i})
            onset_cell22=[onset_cell22,str2num(Time{i})];
        end
        if strfind(Code{i},'cell10')
            display(Time{i})
            onset_cell10=[onset_cell10,str2num(Time{i})];
        end
    end;
      
    %BEGIN SUBTRACTING START TIME AND CONVERTING TO [ms]
    onset_em100_HA=(onset_em100_HA-start_time)/10000/TR;
    onset_em100_FE=(onset_em100_FE-start_time)/10000/TR;
    onset_em40_HA=(onset_em40_HA-start_time)/10000/TR;
    onset_em40_FE=(onset_em40_FE-start_time)/10000/TR;
    onset_cell22=(onset_cell22-start_time)/10000/TR;
    onset_cell10=(onset_cell10-start_time)/10000/TR;
    %END SUBTRACTING START TIME AND CONVERTING TO [ms]
    
    durations={[0],[0],[0],[0]};
    onsets={onset_em100_HA,onset_em100_FE,onset_em40_HA,onset_em40_FE,onset_cell22,onset_cell10};
    names={'em100_HA','em100_FE','em40_HA','em40_FE','cell_22','cell_10'};
    
    save(outfile{1},'names','onsets','durations');
end
