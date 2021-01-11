# return_zddi
ZDDI

#使用教程
#1、将windows_file上传至当前文件夹
#2、使用以下命令开始批量导入
PYTHONPATH=./lib/site-packages/   python main.py  -f <file_name>   -v 3.11 
3、使用以下命令将原始windows文件转换为csv模板
PYTHONPATH=./lib/site-packages/   python main.py  -f <file_name>  -csv  yes   

工具变更记录
2020-6-22增加option16、和option66的全局options参数

2020-9-9增加windows原始文件转换
2020-9-28增加win源文件转换为csv格式
2020-11-2 增加option66/67的option参数识别,并优化csv格式转换
2020-11-3 增加option60的option参数识别

2020-11-9 增加当windows的网络备注缺失一个位时增加异常判断,增加新的utf-16le文件格式自动转换
2020-12-31 增加windows的option42参数识别
