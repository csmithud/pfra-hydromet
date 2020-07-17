from hydromet import*


#---------------------------------------------------------------------------#
def main(forcing_dir: plib, outputs_dir: plib, bin_dir: plib, filename: str, 
                variable: str="Excess-Rainfall", data_type: str='INST-VAL', 
                            units: str='INCHES', remove_temp_files: bool=True, 
                                            display_print: bool=True) -> None:
    '''For each JSON within the forcing directory, the function extracts the
       excess precipitation data for each boundary condition and duration 
       within a given domain's JSON file and saves the data to a single DSS 
       file.

       Parameters
       ----------
       forcing_dir: The path of the forcing directory containing the JSON 
                    files which will be converted to DSS. 
       outputs_dir: The path to the directory where the final DSS file is 
                    saved. 
       bin_dir: The path to the binary directory which contains the dssutl 
                executable. 
       filename: The name of the directory containing the forcing data, as 
                 a string.
       variable: A description of the data representation, as a string, i.e. 
                'Excess-Rainfall'.
       data_type: The type of data, as a string, e.g. 'INST-VAL' corresponds to
                  instantaneous value. 
       units: The units, as a string, of the excess rainfall which will be 
              specified within the final DSS file. 
       remove_temp_files: Bool specifying whether to remove the intermediate 
                          input files generated during the construction of 
                          the final DSS file. 
       display_print: Bool specifying whether to display print statements.     

       Returns
       -------
       None

    '''
    files = []
    temp_files = ['DSSUTL.EXE', 'DSS_MAP.input']
    all_durations = []
    for file in forcing_dir.glob('*.json'):
        files.append(file)
    for file in files:
        if display_print:
            print('Converting {} to DSS...'.format(file.name))
        with open(file) as f:
             data = json.load(f)
        durations = list(data.keys())   
        for dur in durations:
            idx_ord = data[dur]['time_idx_ordinate'].lower()
            idx = data[dur]['time_idx']
            BCNames = list(data[dur]['BCName'].keys())
            for BCN in BCNames:
                pluv_domain = BCN  
                scen_name = '{0}_{1}'.format(pluv_domain, dur)
                df = pd.DataFrame.from_dict(data[dur]['BCName'][BCN])
                df[idx_ord] = idx
                df = df.set_index(idx_ord)
                tstep_dic = determine_tstep_units(df)
                tstep = list(tstep_dic.keys())[0]
                tstep_units = list(tstep_dic.values())[0]
                to_dss = 'ToDSS_{0}.input'.format(dur)
                if dur not in all_durations:
                    all_durations.append(dur)
                    dss_map(outputs_dir, variable, tstep, tstep_units, units,
                                 data_type, to_dss = to_dss, open_op = 'a+')
                    temp_files.append(to_dss)
                excess_df_to_input(outputs_dir, df, tstep, tstep_units, 
                                                    scen_name, 'a+', to_dss) 
    make_dss_file(outputs_dir, bin_dir, filename, remove_temp_files = False, 
                                                display_print = display_print)
    if remove_temp_files:
        for file in temp_files:
            os.remove(outputs_dir/file)       
    return 

if __name__== "__main__":
        main()


#---------------------------------------------------------------------------#    