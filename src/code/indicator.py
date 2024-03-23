"""Class to proccess specific indicators."""
import pandas as pd
import re


class Indicator:
    """Parse indicator characteristics (section, name, unit, code) from xlsx sheet."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize class to parse data
        :param data: DataFrame with data from some xlsx file sheet.
        """
        """Initialize class to parse data"""
        self.section = None
        self.name = None
        self.unit = None
        self.code = None
        self.data = data

    def find_names(self):
        """Search indicator name, section, unit and code in dataframe (first column)."""

        # Ищем все в первой колонке датафрема, который получили из листа файла xlsx
        first_column = self.data.iloc[:, 0].apply(lambda x: ' '.join(x.split()) if not pd.isna(x) else x)
        # Нужная нам инфа до строки, в которой указано Российская Федерация
        text_to_find = "Российская Фед"
        matching_rows = first_column.str.contains(text_to_find).fillna(False)
        index_of_row = matching_rows[matching_rows].index.tolist()
        
        special_for_russia = ''

        if len(index_of_row) == 0:
            text_to_find = "Центральный федеральный округ"
            matching_rows = first_column.str.contains(text_to_find).fillna(False)
            index_of_row = matching_rows[matching_rows].index.tolist()
            index_of_row[0] -= 1
            
            if len(index_of_row) == 0:
                raise ValueError("Name is not found. Russian Federation is not in dataframe.")
        elif len(first_column[index_of_row[0]]) > 22:
            special_for_russia = '; для значений в целом по России: ' + first_column[index_of_row[0]][20:].replace(',', '').strip()

        elif len(index_of_row) == 2:
            raise ValueError("Several rows with Russian Federation.")

        

        """
        Тут под разные варианты xlsx листа разбор. Иногда нужные данные об индикаторе хранятся в разных строках.
        Позиции можно вычислить относительно строки, в которой есть Российская Федерация.
        Внутри if просто аккуратно обрабатываем строки и собираем нужную информацию.
        """
        position = index_of_row[0]
        replacements = {'1)': '', ';2)': '', ';3)': '', ';': ',', 'оквэд': 'ОКВЭД', ' снг': ' СНГ'}

        nulls_before_data = first_column[:position].isnull().sum()
        beginning = 0
        
        for i in range(len(first_column)):
            if first_column.iloc[i] is not pd.NA:
                if first_column.iloc[i][0:5] == 'Социа':
                    beginning = i
                    
        header = [x for x in first_column[beginning + 1 : position] if x is not pd.NA]
        
        self.section = self.process_string(header[0], replacements)
        
        if (header[-1] is pd.NA):
            self.name = ': '.join(self.process_string(x, replacements) for x in header[1:-1])
            self.code = ''.join([part.zfill(2) for part in re.match(r'^[\d.]+', header[-2]).group().split('.')]).ljust(8,'0')
            self.unit = ''
        elif (header[-1][0] == '('):
            self.name = ': '.join(self.process_string(x, replacements) for x in header[1:-1])
            self.code = ''.join([part.zfill(2) for part in re.match(r'^[\d.]+', header[-2]).group().split('.')]).ljust(8,'0')
            self.unit = header[-1].strip("()").replace(';', ',') + special_for_russia
        else:
            self.name = ': '.join(self.process_string(x, replacements) for x in header[1:])
            self.code = ''.join([part.zfill(2) for part in re.match(r'^[\d.]+', header[-1]).group().split('.')]).ljust(8,'0')
            self.unit = ''
 

        return self.section, self.name, self.unit, self.code

    def lower_sentence(self, sentence: str):
        """
        Strip string and change all characters except first to lowercase.
        :param sentence:
        :return:
        """
        sentence = sentence.strip()
        return sentence[0] + sentence[1:].lower()


    def process_string(self, sentence: str, repl: dict):
        """
        Process string and remove non-importamt items.
        :param sentence:
        :param repl:
        :return:
        """
        if sentence == '' or sentence is pd.NA:
            return ''
        sentence = re.sub(r'^[\d.]+', '', sentence.strip())
        sentence = self.lower_sentence(sentence)
        for old_value, new_value in repl.items():
            sentence = sentence.replace(old_value, new_value)

        return sentence

if __name__ == '__main__':
    pass