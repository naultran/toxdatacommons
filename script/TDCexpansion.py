import warnings
import pandas as pd


from io import StringIO




warnings.filterwarnings("ignore", category=UserWarning)

class Gen3process:
    # process data extracted from gen3
    def __init__(self, sub):
        self.sub = sub

    def process_node_data(self, node_name, keys, program, project, fileformat='tsv', external_links=[]):
        # process the node data and return a dataframe
        data = self.sub.export_node(program=program, project=project, node_type=node_name, fileformat=fileformat)
        if fileformat == 'json':
            data = self.remove_newlines(data)
            node_df = pd.json_normalize(data['data'])
            for external_link in external_links:
                node_df = node_df.explode(external_link)
                node_df[f'{external_link}.id']=node_df[external_link].apply(lambda x: x['node_id'])
                node_df[f'{external_link}.submitter_id']=node_df[external_link].apply(lambda x: x['submitter_id'])
                node_df = node_df.drop(external_link, axis=1)
        else:
            node_df = pd.read_csv(StringIO(data), sep='\t', header=0)
        
        for key in keys:
            node_df[key] = node_df[key].str.split(',')
            node_df = node_df.explode(key)
        pattern = r'(^|\.)id($|\.)'
        drop_columns = [col for col in node_df.columns if pd.Series(col).str.contains(pattern).any()]
        node_df = node_df.drop(drop_columns, axis=1)
        node_df = node_df.reset_index(drop=True)
        return node_df

    def get_unique_values(self,dataframe, column_name):
        # get unique value
        unique_values = dataframe[column_name].unique()
        unique_string = ','.join(map(str, unique_values))
        return unique_string

    def remove_newlines(self, obj):
        # remove new lines
        if isinstance(obj, dict):
            return {key: self.remove_newlines(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.remove_newlines(element) for element in obj]
        elif isinstance(obj, str):
            return obj.replace('\n', '').replace('\r', '')
        else:
            return obj

    def rename_overlapping(self, dataframes, separator='.'):
        # rename the overlapping columns
        for i, (node_names, df) in enumerate(dataframes):
            overlapping_columns = set(df.columns) & set(column for _, other_df in dataframes[i+1:] for column in other_df.columns)
            for column in overlapping_columns:
                # Ignore the column named "submitter_id"
                if "submitter_id" in column:
                    continue
                else: 
                    new_column_name = f"{node_names}{separator}{column}"
                    df.rename(columns={column: new_column_name}, inplace=True)
                    for _, other_df in dataframes[i+1:]:
                        if column in other_df.columns:
                            other_df.rename(columns={column: f"{_}{separator}{column}"}, inplace=True)
            df.rename(columns={'submitter_id': f"{node_names}{separator}submitter_id"}, inplace=True)
        return dataframes

    def merge_dataframes(self, dataframes):
        # merge multiple dataframes based on submitter_id
        merged_df = None
        unmerged = dataframes
        while unmerged:
            loop_dataframes = unmerged
            for i, (node_names, df) in enumerate(loop_dataframes):
                if merged_df is None:
                    merged_df = df
                    unmerged.remove((node_names, df))
                else:
                    common_columns = list(set(merged_df.columns) & set(df.columns))
                    if common_columns:
                        merged_df = pd.merge(merged_df, df, on=common_columns)
                        unmerged.remove((node_names, df))
                
        return merged_df 


    def build_study(self, program, project, studies_to_match):
        # build study dataframe
        # STUDY NODE
        study_df = self.process_node_data('study', ['submitter_id'], program=program, project=project)
        if studies_to_match:
            study_df = study_df[study_df['submitter_id'].isin(studies_to_match)]

        # CONTACT NODE
        contact_df = self.process_node_data('contact', ['studies.submitter_id'], program=program, project=project) 
        
        # FUNDING NODE
        funding_df = self.process_node_data('funding', ['studies.submitter_id'], program=program, project=project) 
        
        # PUBLICATION NODE
        publication_df = self.process_node_data('publication', ['studies.submitter_id'], program=program, project=project)
        
        # rename the overlap column except the submitter_id and merge them
        dataframes = [('studies', study_df),('contacts', contact_df), ('fundings', funding_df), ('publications', publication_df) ]
        merged_df = self.merge_dataframes(self.rename_overlapping(dataframes=dataframes))

        return merged_df

    def build_subject(self, program, project, studies_to_match, subjects_to_match):
        # build subject dataframe
        # SUBJECT NODE
        subject_df = self.process_node_data('subject', ['studies.submitter_id'], program=program, project=project)
        if studies_to_match:
            subject_df = subject_df[subject_df['studies.submitter_id'].isin(studies_to_match)]

        # HOUSING NODE
        housing_df = self.process_node_data('housing', ['subjects.submitter_id'], program=program, project=project) 
        
        # DIET NODE
        diet_df = self.process_node_data('diet', ['housings.submitter_id'], program=program, project=project) 
        
        # TREATMENT NODE
        treatment_df = self.process_node_data('treatment', ['subjects.submitter_id'], program=program, project=project) 

        # rename the overlap column except the submitter_id and merge them
        dataframes = [('subjects', subject_df),('housings', housing_df), ('diets', diet_df), ('treatments', treatment_df) ]
        merged_df = self.merge_dataframes(self.rename_overlapping(dataframes=dataframes))

        ## Calculate animal age
        # Convert the date columns to datetime objects
        merged_df['euthanasia_date'] = pd.to_datetime(merged_df['euthanasia_date'])
        merged_df['start_date'] = pd.to_datetime(merged_df['start_date'])

        # Calculate the number of days between the two dates
        merged_df['num_days'] = (merged_df['euthanasia_date'] - merged_df['start_date']).dt.days

        # Add the values from another column, assuming the column is called 'another_column'
        merged_df['age'] = merged_df['num_days'] + merged_df['start_date_age']
        
        return merged_df

    def build_sample(self, program, project, subjects_to_match):
        # build sample dataframe
        # SAMPLE NODE
        sample_df = self.process_node_data('sample', ['subjects.submitter_id'], program=program, project=project)
        if subjects_to_match:
            sample_df = sample_df[sample_df['subjects.submitter_id'].isin(subjects_to_match)]

        # ALIQUOT NODE
        aliquot_df = self.process_node_data('aliquot', ['samples.submitter_id'], program=program, project=project)
        
        # MASS_SPEC_ASSAY NODE
        ms_assay_df = self.process_node_data('mass_spec_assay', ['aliquots.submitter_id'], program=program, project=project, fileformat='json', external_links=['aliquots'])
        
        # MS_RAW_DATA NODE
        ms_raw_data_df = self.process_node_data('ms_raw_data', ['mass_spec_assays.submitter_id'], program=program, project=project)
        
        # rename the overlap column except the submitter_id and merge them
        dataframes = [('samples', sample_df),('aliquots', aliquot_df), ('mass_spec_assays', ms_assay_df), ('ms_raw_datas', ms_raw_data_df) ]
        merged_df = self.merge_dataframes(self.rename_overlapping(dataframes=dataframes))


        return merged_df