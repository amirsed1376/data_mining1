import xlrd
import sqlite3
import time

class SqlManager:
    def __init__(self , file):
        self.conn = sqlite3.connect(file)
        self.crs = self.conn.cursor()

    def create_database(self):
        self.crs.execute(("CREATE TABLE IF NOT EXISTS transactions("
                          "InvoiceNo VARCHAR(100) NOT NULL  ,"
                          "StockCode VARCHAR(100) ,"
                          "Description VARCHAR(200) NOT NULL ,"
                          "Quantity INT NOT NULL  ,"
                          "InvoiceDate VARCHAR(100) ,"
                          "UnitPrice FLOAT(6,3) NOT NULL ,"
                          "CustomerID INT ,"
                          "Country VARCHAR(100) "
                          ")"))
        self.conn.commit()
        self.crs.execute("CREATE TABLE IF NOT EXISTS transactions2("
                         "InvoiceNo VARCHAR(100) NOT NULL ,"
                         "Descriptions VARCHAR(1000) NOT NULL"
                         ")")
        self.conn.commit()


    def excel_to_sql(self, excel_name, sheet_name):

        wb = xlrd.open_workbook(excel_name + ".xlsx")
        sheet = wb.sheet_by_index(0)

        for row in range(1, sheet.nrows):
            try:
                query = "INSERT INTO transactions values ("
                for index in range(8):
                    try:
                        data=sheet.cell_value(row, index)
                        if data is None:
                            raise Exception("empty ")
                        if len(str(data).strip())==0:
                            raise Exception("empty")
                        if str(data).strip().lower() == "manual":
                            raise Exception("MANUAL")
                        data = str(data).replace('"',"'")
                        if index == 3 or index == 5 or index == 6:
                            if float(data) < 0:
                                raise Exception("negetive number ")
                            query += str(data) + ' , '
                        elif index == 7:
                            query += '"' + str(data).strip() + '"'

                        else:
                            query += '"' + str(data).strip() + '" , '

                    except Exception as e:
                        print(e)
                        raise e

                query += ")"
                self.crs.execute(query)
            except Exception as e:
                print(data)
                print(row , e)
        self.conn.commit()





if __name__ == '__main__':
    start_time=time.time()
    sql_manager = SqlManager("information.sqlit")
    sql_manager.create_database()
    sql_manager.excel_to_sql(excel_name="Online_Shopping", sheet_name="Online Retail")
    print("TIME=",time.time()-start_time)
