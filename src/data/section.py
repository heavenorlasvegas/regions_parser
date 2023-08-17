import pandas as pd
from comment import Comment
from indicator import Indicator
from periods import Periods
from objects import ObjectInfo
import re


class Section:
    """Parse data for a give section (xml file)."""
    def __init__(self, source: str, regions_dict: str):
        """
        Initialize class.
        :param source: Path to source file with data about specific section.
        :param regions_dict: Path to reference regions dictionary.
        """
        self.source = source
        self.regions_dict = regions_dict
        self.sheets = self.sheet_names()
        self.data = None

    def sheet_names(self):
        """
        Return list of xlsx file sheets except first sheet.
        :return: List with sheets names.
        """
        return pd.ExcelFile(self.source).sheet_names[1:]

    def process_section(self):
        """
        Process xlsx file sheet by sheet. Save all date to one dataframe.
        :return:
        """
        df = pd.DataFrame()
        for sheet in self.sheets:
            print("Parse list ", sheet, ' of file ', self.source)
            data = self.process_sheet(sheet)
            df = pd.concat([df, pd.DataFrame(data)], axis=0)

        self.data = df
        return df

    @staticmethod
    def skip_value(val):
        if val in ('…', ' - ', '-', ' -', '- ', '...',  '–', '..',
                   '….', '−', '        …', '... ', '...  ', ' ...', '‐'):
            return True
        return False


    def process_sheet(self, sheet_name: str):
        """
        Parse all data from specific xlsx sheet.
        :param sheet_name: Name of sheet to parse.
        :return: Dictionary with indicator values from the sheet and other information.
        """
        result = {'section': [],
                  'indicator_name': [],
                  'indicator_unit': [],
                  'indicator_code': [],
                  'object_name': [],
                  'object_level': [],
                  'object_oktmo': [],
                  'object_okato': [],
                  'year': [],
                  'indicator_value': [],
                  'comment': [],
                  'subsection': [] # добавляем subsection - здесь под-секции для каждого года в таблицах, где на год приходится несколько столбцов
                }

        df = pd.read_excel(self.source, sheet_name=sheet_name, dtype='string')

        indicator = Indicator(df)
        indicator.find_names()
        print("Section is: ", indicator.section, " Indicator is: ", indicator.name, " Unit is: ", indicator.unit)

        comment = Comment(df)
        comment.find_comment()

        periods = Periods(df)
        periods.check_periods()

        objects = ObjectInfo(df, self.regions_dict)
        objects.compare_etalon()

        for key, info in objects.objects.items():
            for year in range(2000, 2022):
              n_it = len(periods.periods[year]) if year in periods.periods.keys() and type(periods.periods[year]) == list else 1
              # итерируемся столько раз, сколько подсекций есть на каждый год: если в словаре с годами значения это списки, то длина списка, если нет, то 1
              # ВАЖНО: в некоторых таблицах у разных годов разное количество подсекций, поэтому n_it считаем для каждого года отдельно
              for i in range(n_it):
                result['section'].append(indicator.section)
                result['indicator_name'].append(indicator.name)
                result['indicator_unit'].append(indicator.unit)
                result['indicator_code'].append(indicator.code)
                result['object_name'].append(key)
                result['object_level'].append(info[0])
                result['object_oktmo'].append(info[1])
                result['object_okato'].append(info[2])
                result['year'].append(year)
                result['comment'].append(comment.comment)

                # если есть несколько годов, то есть под-секция, здесь она добавляется
                if type(periods.periods[list(periods.periods.keys())[i]]) == list:
                    result['subsection'].append(df.loc[periods.row +1 , periods.periods[year][i]])
                else:
                    result['subsection'].append('No subsection')

                #Handling some unsusual values which can't be save as floats.
                if year in periods.periods.keys():
                  # тут если есть под-секция, то тяну значение из под-секции, если нет, то беру значение столбца заданного года
                  if type(periods.periods[year]) == list:
                    value = df.loc[info[3], periods.periods[year][i]]
                  else:
                    value = df.loc[info[3], periods.periods[year]]

                  if pd.isna(value):
                        value = -99999999
                  elif self.skip_value(value):
                        value = -88888888
                  elif ' р.' in value:
                        value = round(float(value.replace('в ', '').replace(' р.', '').replace(',', '.').strip())*100, 4)
                  elif ')' in value:
                        value = re.sub(r'\d[)]', '', str(value.replace(',', '.')))
                        value = -88888888 if self.skip_value(value) else round(float(value), 4)
                  else:
                      try:
                            value = round(float(value), 4)
                      except ValueError:
                            value = re.sub(r'\s+', '', str(value).replace(',', '.'))
                            value = round(float(value), 4) if (not self.skip_value(value)) and (value.isnumeric()) else -88888888

                else:
                    value = -99999999

                result['indicator_value'].append(value)
        return result


if __name__ == '__main__':
    pass