import xlsxwriter
from SqlManager import SqlManager
import ExcelManager 
import itertools
from itertools import combinations, chain

def read_fitem_set(excel_name , sheet_name , base):
    info = ExcelManager.read_rows(excel_name, sheet_name, base)
    freq = []
    for row in range(2, len(info)):
        temp = []
        for val in info[row]:
            if val != None:
                temp.append(val)
        freq.append(temp)
    return freq
def find_itemSet_frequentCount(sql_file, data):
    sql_manager = SqlManager(sql_file)
    itemSet_count = {}
    transactions_length = sql_manager.crs.execute('select count(InvoiceNo) from transactions2').fetchall()[0][0]
    for itemset in data:
        query = 'select count(Descriptions) from transactions2 where '
        temp = ''
        for item in itemset:
            query += 'Descriptions like ' + '"%' + str(item).replace('"', "'") + '%" and '
            temp += str(item) + ','
        query = query[:-4]
        result = sql_manager.crs.execute(query).fetchall()[0][0]
        temp = temp[:-1]
        itemSet_count[temp] = result
    return itemSet_count, transactions_length
def make_rule(sql_file, data, minconf):
    rules = []
    lefts = []
    rights =[]
    lifts = []
    confs = []
    itemSet_count, transactions_length = find_itemSet_frequentCount(sql_file, data)
    for k in itemSet_count.keys():
        length = len(k.split(','))
        sup_itemset = itemSet_count.get(k)
        if length > 1:
            item_set = k.split(',')
            result = make_sub_set(item_set, length - 1)
            for r in result:
                leftRull = ''
                rightRull = ''
                for left in r[0]:
                    leftRull += left + ','
                for right in r[1]:
                    rightRull += right + ','

                leftRull = leftRull[:-1]
                rightRull = rightRull[:-1]

                sup_left = itemSet_count.get(leftRull, 10000)
                sup_right = itemSet_count.get(rightRull, 10000)

                if float(sup_itemset / sup_left) > float(minconf):
                    conf = float(sup_itemset / sup_left)
                    lift = (conf * transactions_length) / sup_right
                    rule = leftRull + '--->' + rightRull
                    if rule not in rules:
                        rules.append(rule)
                        lefts.append(leftRull)
                        rights.append(rightRull)
                        lifts.append(lift)
                        confs.append(conf)

                if float(sup_itemset / sup_right) > float(minconf):
                    conf = float(sup_itemset / sup_right)
                    lift = (conf * transactions_length) / sup_left
                    rule = rightRull + '--->' + leftRull
                    if rule not in rules:
                        rules.append(rule)
                        lefts.append(leftRull)
                        rights.append(rightRull)
                        lifts.append(lift)
                        confs.append(conf)

    return confs, lifts,  rules, lefts, rights

def make_rule_excel(confs, lifts, rules, lefts, rights, excel_name, sheet_name, base_address):

    workbook = xlsxwriter.Workbook(base_address + '\\' + excel_name + '.xlsx')
    worksheet = workbook.add_worksheet(sheet_name)
    worksheet.write('A1', 'Left')
    worksheet.write('B1', 'Right')
    worksheet.write('C1', 'Rule')
    worksheet.write('D1', 'Confidence')
    worksheet.write('E1', 'Lift')
    for i in range(0, len(rules)):
        worksheet.write(i+1, 0, lefts[i])
        worksheet.write(i+1, 1, rights[i])
        worksheet.write(i+1, 2, rules[i])
        worksheet.write(i+1, 3, confs[i])
        worksheet.write(i+1, 4, lifts[i])
    workbook.close()


def make_sub_set(l, number):
    l1 = list(map(set, itertools.combinations(l, number)))
    result = []
    for i in range(len(l1)):
        result.append((list(l1[i]), [x for x in l if x not in list(l1[i])]))
    return result

if __name__ == '__main__':
    min_cof = 0.4
    min_sup=0.02
    fitemset = read_fitem_set('apriori', str(min_sup), 'outs')
    confs, lifts, rules, lefts, rights, = make_rule("information.sqlit",fitemset, min_cof)
    make_rule_excel(confs, lifts, rules, lefts, rights, 'rule', str(min_cof), 'outs')
    print("finish")
