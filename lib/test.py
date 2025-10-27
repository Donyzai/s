from swc_cinfo import cpu_usage
import time
FILE_PATH = 'cpu_usage.txt'
MAX_LINES = 20

def append_data(new_line):

    # 首先把数据写入文件中
    with open(FILE_PATH,'a',encoding='utf-8') as f:
        f.write(new_line + '\n')
    
    # 读取文件中总行数
    with open(FILE_PATH,'r',encoding='utf-8') as f:
        lines = f.readlines()

    # 判断是否超过最大值
    if len(lines) > MAX_LINES:
        lines = lines[len(lines)-MAX_LINES:]

        with open(FILE_PATH,'w',encoding='utf-8') as f:
            f.writelines(lines)

if __name__ == '__main__':
    # 
    [append_data(str(i)) for i in range(0,100)]


# # 创建1000个数字至文件
# with open(FILE_PATH,'a',encoding='utf-8') as f:
#     [f.write(str(i)+'\n') for i in range(1000,1200)]
