from SqlManager import SqlManager
from  find_items_information import find_items_count,find_transactions
import time
import os
import errno
import ExcelManager
from Rule import read_fitem_set,make_rule,make_rule_excel
from Eclat import Eclat

def make_country_databases( sql_folder):
    sql_manager = SqlManager("information.sqlit")
    countries_query = sql_manager.crs.execute("select distinct Country from transactions ").fetchall()
    countries = [x[0] for x in list(countries_query)]
    for country in countries:
        sql_manager2 = SqlManager(sql_folder + str(country).replace(" ", "_") + ".sqlit")
        sql_manager2.create_database()
        sql_query = sql_manager.crs.execute(
            'select * from transactions where Country = "' + str(country) + '"').fetchall()
        values = str(sql_query)[1:len(str(sql_query)) - 1]
        sql = "INSERT INTO transactions values " + values
        sql_manager2.crs.execute(sql)
        sql_manager2.conn.commit()

def makeFolder( address):
    try:
        os.makedirs(address)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


class EachCountry:
    def __init__(self,base_folder ,country ,outs_folder ):
        self.base_folder=base_folder
        self.country=country
        outs_folder = outs_folder + country
        makeFolder(outs_folder)
        outs_folder += "\\"
        self.outs_folder=outs_folder
        self.database_address=base_folder+country+".sqlit"



    def find_items_information_countries(self,sqls_folder , country):
        # find_items_information

        time1 = time.time()
        Invoice_Item = find_transactions(sql_file=self.database_address, save_excel_name="VoiceNo_Item",
                                         save_sheet="transactions", out_folder=self.outs_folder)

        print("TIME", time.time() - time1)
        print("finish")


    def eclat_country(self, minsup):
        ExcelManager.create_sheet(excel_name="eclat", sheet_name=str(minsup), columns_name=[], base_address=self.outs_folder)
        start_time = time.time()
        eclat = Eclat(self.database_address, minsup)
        large_items = eclat.eclat()
        ExcelManager.add_rows(excel_name="eclat", sheet_name=str(minsup), base_address=self.outs_folder,
                              datas=[["minsup", str(minsup)], ["time", str(time.time() - start_time)]])

        for k, LK in enumerate(large_items):
            if len(LK) != 0:
                save_list = [x[0] for x in LK]
                ExcelManager.add_rows(excel_name="eclat", sheet_name=str(minsup), base_address=self.outs_folder,
                                      datas=save_list)

        print("finish minsup =", minsup)



    def rules_country(self,min_cof ,min_sup):
        fitemset = read_fitem_set('eclat', str(min_sup), self.outs_folder)
        confs, lifts, rules, lefts, rights, = make_rule(self.database_address, fitemset, min_cof)
        make_rule_excel(confs, lifts, rules, lefts, rights, 'rule', str(min_cof), self.outs_folder)
        print("finish")


if __name__ == '__main__':
    sql_folder="sqls"
    makeFolder(sql_folder)
    sql_folder+="\\"
    # make_country_databases(sql_folder) #for create for each database
    sql_manager = SqlManager("information.sqlit")
    countries_query = sql_manager.crs.execute("select distinct Country from transactions ").fetchall()
    countries = [x[0] for x in list(countries_query)]
    for country in countries:
        each_country = EachCountry(sql_folder,str(country).replace(" ","_"),"outs\\")
        each_country.find_items_information_countries(sql_folder,str(country).replace(" ","_"))
        each_country.eclat_country(minsup=0.07)
        each_country.rules_country(min_cof=0.3 , min_sup=0.07)
        print(country ," finished ")




