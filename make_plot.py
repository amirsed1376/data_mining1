import xlrd
import matplotlib.pyplot as plt


def read_fitem_set(excel_name, base):
    wb = xlrd.open_workbook(base + excel_name, on_demand=True)
    sup_time = {}
    for i in range(len(wb.sheet_names())):
        sheet = wb.sheet_by_index(i)
        sup_time[sheet.cell_value(0, 1)] = float(sheet.cell_value(1, 1))
    return sup_time

def make_alg_plot(sup_time, algorithm, out_folder):

    fig, axs = plt.subplots()
    plt.ylabel('Tims S')
    plt.xlabel('Min_Support')
    axs.bar(tuple(sup_time.keys()), sup_time.values())
    fig.suptitle(algorithm, fontsize=30)
    plt.savefig(out_folder + algorithm)


if __name__ == '__main__':
    loc = "apriori.xlsx"
    outs_folder = "outs\\"
    sup_time = read_fitem_set(excel_name=loc, base=outs_folder)
    make_alg_plot(sup_time,  algorithm='apriori', out_folder=outs_folder)
