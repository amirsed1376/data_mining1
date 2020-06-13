import xlrd
import xlsxwriter
import matplotlib.pyplot as plt
import ExcelManager
from SqlManager import SqlManager
import time


# read data set
def find_transactions(sql_file, save_excel_name="new_file", save_sheet="new_sheet",
                      out_folder=""):
    """question 1
    this function find transactions from a sheet and save to a new xlsx file
    """
    print("FIND TRANSACTION")
    InvoiceNo_Item = {}

    sql_manager = SqlManager(sql_file)

    invoice_nos = sql_manager.crs.execute("select distinct InvoiceNo  from transactions ").fetchall()
    for invoice_no in list(invoice_nos):
        invoice_no_str = str(invoice_no[0])
        InvoiceNo_Item[invoice_no_str] = []

    sql_result = sql_manager.crs.execute("select distinct InvoiceNo,Description  from transactions ").fetchall()
    for invoice_no in list(sql_result):
        invoice_no_str = str(invoice_no[0])
        InvoiceNo_Item[invoice_no_str].append(invoice_no[1])


    # Create xlsx
    workbook = xlsxwriter.Workbook(out_folder + save_excel_name + ".xlsx")
    worksheet = workbook.add_worksheet(save_sheet)


    # Write InvoiceNo And Item Into xlsx .
    row = 0
    col = 0
    for InvoiceNo in InvoiceNo_Item:
        sql="INSERT INTO transactions2 values ( "+str(InvoiceNo)+ ', "'
        worksheet.write(row, col, InvoiceNo)
        items_string=""
        for item in InvoiceNo_Item[InvoiceNo]:
            items_string+="**"+str(item)
            col += 1
            worksheet.write(row, col, item)
        items_string+='" )'
        sql += items_string
        sql_manager.crs.execute(sql)
        col = 0
        row += 1
    sql_manager.conn.commit()

    workbook.close()
    return InvoiceNo_Item


def find_items_count(sql_file, save_fig="Item_Frequency", number_of_best_item=1,
                     save_excel_name="Item_Frequency", out_folder=""):
    print("FIND ITEM COUNT")
    """question2
    this function find count of each items and print them  and save plot of it

    """

    item_names = []
    information = []
    item_frequencies = []
    best_item_names = []
    best_item_frequencies = []

    sql_manager = SqlManager(sql_file)
    sql_result = sql_manager.crs.execute(
        "select  sum(Quantity) from transactions ").fetchall()
    total_item = int(sql_result[0][0])

    sql_result = sql_manager.crs.execute(
        "select  Description,sum(Quantity) from transactions group by Description ORDER BY sum(Quantity) DESC;").fetchall()

    for index, item in enumerate(sql_result):
        information.append([item[0], item[1], item[1] / total_item])
        item_names.append(item[0])
        item_frequencies.append(item[1] / total_item)
        if index < number_of_best_item:
            best_item_names.append(item[0])
            best_item_frequencies.append(item[1] / total_item)

    print("total item is : ", total_item)

    # save frequency excel
    ExcelManager.delet_excel(excel_name=save_excel_name, base_address=out_folder)
    ExcelManager.create_sheet(excel_name=save_excel_name, sheet_name=save_excel_name,
                              columns_name=["item", "count", "Item_Frequency"], base_address=out_folder)
    ExcelManager.add_rows(excel_name=save_excel_name, sheet_name=save_excel_name, datas=information,
                          base_address=out_folder)

    # save figure of items

    fig, axs = plt.subplots(figsize=(250, 50))
    plt.xticks(rotation=60, fontsize=20)
    plt.yticks(fontsize=20)
    axs.bar(item_names, item_frequencies)
    fig.suptitle('Item_Frequency', fontsize=30)
    plt.savefig(out_folder + save_fig)

    # save figure of best items

    fig, axs = plt.subplots(figsize=(100, 50))
    plt.xticks(rotation=60, fontsize=20)
    plt.yticks(fontsize=20)
    axs.bar(best_item_names, best_item_frequencies)
    fig.suptitle('best Item_Frequency', fontsize=30)
    plt.savefig(out_folder + "best_" + save_fig)


if __name__ == '__main__':
    loc = "Online_Shopping.xlsx"
    outs_folder = "outs\\"
    time1 = time.time()
    Invoice_Item = find_transactions(sql_file="information.sqlit", save_excel_name="VoiceNo_Item",
                                     save_sheet="transactions", out_folder=outs_folder)
    find_items_count(sql_file="information.sqlit", number_of_best_item=10, save_excel_name="ferequency",
                     out_folder=outs_folder)

    print("TIME", time.time() - time1)
    print("finish")
