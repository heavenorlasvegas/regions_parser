import pandas as pd

class Periods:
    """Find on xlsx sheets what periods (years) are available."""
    def __init__(self, data: pd.DataFrame):
        """
        Initialize class to find available years.
        :param data: DataFrame with data from some xlsx file sheet.
        """
        self.periods = None # Here we save available periods in dictionary (year - column with data for this year format)
        self.data = data
        self.row = None

    def check_periods(self):
        """
        Here find row with years and save all available years.
        :return:
        """

        year_column = self.data.iloc[:, 0].apply(lambda x: True if pd.isna(x) else False)
        index_of_row = year_column[year_column].index.tolist()

        if len(index_of_row) == 0:
            raise ValueError("Period string is not find.")
        elif len(index_of_row) >= 2:
            row = None
            for el in index_of_row:

                if not pd.isna(self.data.iloc[el, 1]): # заменила 2 на 1, потому что в таблицах, где на год по одному столбцу 1 тоже заполнен, а в тех, где на год по несколько столбцов, заполнен только 1
                    if self.data.iloc[el, 1].startswith('2'): #аналогично
                        row = el
                        self.row = row #добавляю атрибут row, чтобы потом удобно было отсылаться к строке с годами (позволяет подтягивать подсекции)
                    else:
                        pass
                else:
                    pass
            if not row:
                raise ValueError("Period string is not find.")

            # тут заполняем строку годов
            # по дефолту если на год приходится, например, 3 столбца, то таблица выглядит как
            #| 2000 | <NA> |  <NA> |
            # заполняем их, чтобы было
            #| 2000 | 2000 |  2000 |
            years_row = self.data[row:row+1].T[row].fillna(method = 'ffill').to_list()
            for i in range(len(self.data.columns)):
              self.data[self.data.columns[i]][row] = years_row[i]

            year_values = {}
            for j, i in self.data.iloc[row][1:].items():
              year_values.setdefault(int(i.strip()[0:4]), []).append(j)
            self.periods = year_values
            return year_values
        else:
            year_list = [y for y in self.data.iloc[index_of_row[0]][1:].items() if str(y[1]) != '<NA>']
            year_values = {int(i.strip()[0:4]): j for (j, i) in year_list}
            self.periods = year_values
            self.row = index_of_row[0]
            return year_values


if __name__ == '__main__':
    pass