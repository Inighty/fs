# importing the required modules
import glob
import pandas as pd

# specifying the path to csv files
path = "E:\download\Compressed\m.pcbaby.com.cn_百度移动关键词排名_20220708191221"

# csv files in the path
file_list = glob.glob(path + "/*.xls")

# list of excel files we want to merge.
# pd.read_excel(file_path) reads the excel
# data into pandas dataframe.
excl_list = []

for file in file_list:
    excl_list.append(pd.read_excel(file))

# create a new dataframe to store the
# merged excel file.
excl_merged = pd.DataFrame()

for excl_file in excl_list:
    # appends the data into the excl_merged
    # dataframe.
    excl_merged = excl_merged.append(
        excl_file, ignore_index=True)

# exports the dataframe into excel file with
# specified name.
excl_merged.to_excel('total_food_sales.xlsx', index=False)