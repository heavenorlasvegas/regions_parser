import pandas as pd
import yaml
import re
import numpy as np

class Comment:
    """Find special footnotes and comments in DataFrame prepared from xlsx sheet."""
    def __init__(self, data: pd.DataFrame, indicator: str, sheet: str):
        """
        Intialize class to find footnotes.
        :param data: DataFrame with data from some xlsx file sheet.
        """
        self.comment = '' # Save here processed text of all footnotes.
        self.data = data
        self.indicator = indicator.lower().strip()
        self.sheet = sheet

    def find_comment(self):
        """
        Find all comments in dataframe (strings begining with '*)' chatacters, where * is digit.
        :return: All comments in one string.
        """

        substring_list = ["1)", "2)", "3)", "4)", "5)", "6)", "7)", "8)"]
        superscript_map = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁾', '0123456789)') # To correctly process superscript characters
        self.data = self.data.applymap(lambda cell: cell.translate(superscript_map) if not pd.isna(cell) else cell)
        comments = []

        for comm_number in substring_list:
            text = ''
            matching_cells = self.data.applymap(lambda cell: self.check_substring(cell, comm_number))
            matching_cells = matching_cells.stack()
            comment_locations = list(matching_cells[matching_cells].index) # list of tuples: (row, column) for the cells with comments
            
            if len(comment_locations):
                comment_rows = [cell[0] for cell in comment_locations[:-1]]
                comment_columns = [cell[1] for cell in comment_locations[:-1]]
                comment_cells = [self.clean_comment(self.data.loc[cell], comm_number) for cell in comment_locations[:-1]]
                comment_text = self.data.loc[comment_locations[-1]].replace(comm_number, '').strip()
                comment_for_indicator = all([c[0:10].lower() in self.indicator for c in comment_cells])  
                                
                self.sheet = self.sheet.strip()
                if self.sheet[-1] == '.':
                    comm_num = self.sheet + comm_number[0]
                else:
                    comm_num = self.sheet + '.' + comm_number[0]
                
                if comment_for_indicator:
                    comments.append({
                        'comment_for': np.nan,
                        'comment_number': comm_num,
                        'comment_text': comment_text
                    })
                    
                else:
                    for c in range(len(comment_cells)):
                        
                        comment_for = comment_cells[c]
                        
                        if comment_for in ['...', '…']:
                            comments.append({
                                'comment_for': self.data.loc[comment_rows[c], 'Unnamed: 0'],
                                'comment_number': comm_num,
                                'comment_text': comment_text
                            })  
                        elif comment_for[0:10].lower() in self.indicator:
                            comments.append({
                                'comment_for': 'Вся страна',
                                'comment_number': comm_num,
                                'comment_text': comment_text
                            })  
                        elif (comment_columns[c] == 'Unnamed: 0') and (comment_rows[c] <= comment_rows[-1]) and(len(comment_for) < 50):
                            comments.append({
                                'comment_for': comment_for,
                                'comment_number': comm_num,
                                'comment_text': comment_text
                            })  
                        else:
                            comments.append({
                                'comment_for': '–',
                                'comment_number': comm_num,
                                'comment_text': comment_for + ': ' + comment_text
                            })  
                     
        self.comments = comments                
        return self.comments

    def check_substring(self, cell, number: str):
        """Check is data in cell is string and substring with footnote number is in it."""
        match = number.replace(')', '\)')
        if isinstance(cell, str) and re.search(f"(?<!\.){match}(?!\.|\s\(|\sОКВ)", cell):
            return True
        return False
    
    def clean_comment(self, comment, comm_number):
        comment = comment.replace(comm_number, '').strip()
        if re.search("^\d+$", comment):
            return comment
        return re.sub(r'\s+', ' ', 
                      re.sub(r'^[\s\d.]+', '', 
                             re.sub(r'[\;\,\d\.\)\s]+$', '', 
                                    comment
                                   )
                            )
                     )