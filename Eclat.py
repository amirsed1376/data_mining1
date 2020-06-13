from SqlManager import SqlManager
import time
import ExcelManager


class Eclat:
    def __init__(self, sql_file, minsup):
        self.sql_manager = SqlManager(sql_file)
        self.minsup = minsup
        invoice_nos = self.sql_manager.crs.execute("select DISTINCT  InvoiceNo from transactions ")
        self.total_item = len(list(invoice_nos))
        print("TOTAL ", self.total_item)
        self.minsup_count = self.minsup * self.total_item
        print(self.minsup_count)

    def eclat(self):
        L = [[], []]

        descriptions_query = self.sql_manager.crs.execute("select distinct Description from transactions").fetchall()
        descriptions_dict = {}
        for description in descriptions_query:
            descriptions_dict[str(description[0])] = []

        sql_result = self.sql_manager.crs.execute("select  InvoiceNo,Description  from transactions ").fetchall()
        for row in list(sql_result):
            description = str(row[1])
            descriptions_dict[description].append(str(row[0]))

        for description in descriptions_dict.keys():
            if len(descriptions_dict[description]) > self.minsup_count:
                L[1].append(([str(description)], descriptions_dict[str(description)]))

        print(len(L[1]))
        start_time = time.time()
        print("finding L for k=", 1)
        k = 2
        while len(L[k - 1]) != 0:
            L.append([])
            print("finish and TIME=", time.time() - start_time)
            print("finding L for k=", k)

            start_time = time.time()
            L[k] = self.eclat_gen(L, k)
            k += 1

        return L

    def eclat_gen(self, l, k):
        LK = []
        L = l.copy()
        for index1 in range(len(L[k - 1])):
            l1 = L[k - 1][index1]
            for index2 in range(index1 + 1, len(L[k - 1])):
                l2 = L[k - 1][index2]
                flage = True
                for i in range(k - 2):
                    flage = flage and (l1[0][i] == l2[0][i])
                if flage:
                    try:
                        c = l1[0][:k - 2]
                    except:
                        c = []

                    c.append(l1[0][k - 2])
                    c.append(l2[0][k - 2])
                    if self.has_infrequent_subset(c, l, k):
                        continue
                    else:

                        intersect_list = list(set(l1[1]) & set(l2[1]))

                        if len(intersect_list) > self.minsup_count:
                            LK.append((c, intersect_list))
        return LK

    def has_infrequent_subset(self, c, l, k):
        if k < 3:
            return False
        long_items2 = [x[0] for x in l[2]]
        if [c[-2], c[-1]] in long_items2:
            return False
        else:
            return True


if __name__ == '__main__':

    minsup = 0.02
    ExcelManager.create_sheet(excel_name="eclat", sheet_name=str(minsup), columns_name=[], base_address="outs\\")
    start_time = time.time()
    eclat = Eclat("information.sqlit", minsup)
    large_items = eclat.eclat()
    ExcelManager.add_rows(excel_name="eclat", sheet_name=str(minsup), base_address="outs\\",
                          datas=[["minsup", str(minsup)], ["time", str(time.time() - start_time)]])

    for k, LK in enumerate(large_items):
        if len(LK) != 0:
            save_list = [x[0] for x in LK]
            ExcelManager.add_rows(excel_name="eclat", sheet_name=str(minsup), base_address="outs\\", datas=save_list)

    print("finish minsup =", minsup)
