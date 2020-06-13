from SqlManager import SqlManager
import time
import ExcelManager


class Apriori:
    def __init__(self, sql_file, minsup):
        self.sql_manager = SqlManager(sql_file)
        self.sql_file = sql_file
        self.minsup = minsup

        invoice_nos = self.sql_manager.crs.execute("select DISTINCT  InvoiceNo from transactions ")
        self.total_item = len(list(invoice_nos))
        print("TOTAL ", self.total_item)
        self.minsup_count = self.minsup * self.total_item

    def apriori(self):
        sql_result = self.sql_manager.crs.execute(
            "select  Description,count(Description) from transactions group by Description having count(Description) > " + str(
                self.minsup_count)).fetchall()

        L = [[], []]
        start_time = time.time()
        L[1] = [[x[0]] for x in sql_result]
        print(len(L[1]))
        print("finding L for k=", 1)
        k = 2
        while len(L[k - 1]) != 0:
            print("finish and TIME=", time.time() - start_time)
            print("finding L for k=", k)
            start_time = time.time()
            L.append([])
            CK = self.apriori_gen(L, k)
            for ind, C in enumerate(CK):
                sql = 'select count(distinct InvoiceNo) from transactions2 where '
                for item in C:
                    sql += 'Descriptions like ' + '"%*' + str(item) + '%" and '

                sql = sql[:-4]
                size = self.sql_manager.crs.execute(sql).fetchall()[0][0]
                if size > self.minsup_count:
                    L[k].append(C)

            k += 1

        return L

    def apriori_gen(self, l, k):
        CK = []
        L = l
        for index1 in range(len(l[k - 1])):
            l1 = l[k - 1][index1]
            for index2 in range(index1 + 1, len(l[k - 1])):
                l2 = l[k - 1][index2]
                if l1 == l2:
                    continue
                flage = True
                for i in range(k - 2):
                    flage = flage and (l1[i] == l2[i])
                if flage:
                    try:
                        c = l1[:k - 2]
                    except:
                        c = []
                    c.append(l1[k - 2])
                    c.append(l2[k - 2])
                    if self.has_infrequent_subset(c, l, k):
                        continue
                    else:
                        CK.append(c)
        return CK

    def has_infrequent_subset(self, c, l, k):
        if k < 3:
            return False

        if [c[-2], c[-1]] in l[2]:
            return False
        else:
            return True


if __name__ == '__main__':

    minsup = 0.02
    ExcelManager.create_sheet(excel_name="apriori", sheet_name=str(minsup), columns_name=[], base_address="outs\\")
    start_time = time.time()
    apriory = Apriori("information.sqlit", minsup)
    large_items = apriory.apriori()
    ExcelManager.add_rows(excel_name="apriori", sheet_name=str(minsup), base_address="outs\\",
                          datas=[["minsup", str(minsup)], ["time", str(time.time() - start_time)]])

    print(large_items)
    for k, LK in enumerate(large_items):
        if len(LK) != 0:
            ExcelManager.add_rows(excel_name="apriori", sheet_name=str(minsup), base_address="outs\\", datas=LK)

    print("finish minsup =", minsup)
