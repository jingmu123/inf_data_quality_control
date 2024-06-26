import concurrent.futures
from test2_process import process_line
from test2_process import speicalProces
from tqdm import tqdm





# 生成器函数，逐行读取文件
def read_file_line_by_line(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            yield line


# 逐行读取并并行处理文件
def process_file_parallel(input_file_path, output_file_path):
    # 定义一个收集结果的列表
    results = []
    sp = speicalProces()
    # with open(input_file_path, 'r', encoding='utf-8') as file:
    #     lines = file.readlines()

    # 计算总行数
    total_lines = 100
    results = []

    # 使用线程池并行处理行
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 使用tqdm创建进度条对象
        with tqdm(total=total_lines, desc="Processing lines") as pbar:
            # 将行映射到process_line函数
            # lines = read_file_line_by_line(input_file_path)
            # 重新打开文件以读取内容
            with open(input_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            future_to_line = {executor.submit(process_line, line, sp): idx for idx, line in enumerate(lines)}

            # 为每个完成的任务更新进度条
            for future in concurrent.futures.as_completed(future_to_line):
                try:
                    result = future.result()
                except Exception as exc:
                    print(f'Generated an exception: {exc}')
                else:
                    results.append(result)
                    pbar.update(1)  # 更新进度条
    # 将结果写入新文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.writelines("%s\n" % result for result in results)



# 调用函数
base_dir = "../../../../full_data/guidelines_liangyong_surya/"
save_file = f"{base_dir}/guidelines_liangyong_surya_clean_zh_sample.jsonl"
input_file = f"{base_dir}/guidelines_liangyong_surya_preformat_zh_sample.jsonl"
import time
t1 = time.time()
process_file_parallel(input_file, save_file)
t2=time.time()
print(t2-t1)