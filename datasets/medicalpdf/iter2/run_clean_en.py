from clean_en import process_line
from clean_en import speicalProces
from multiprocessing import Pool, cpu_count
import concurrent.futures
from tqdm import tqdm
import json
import sys
import time


def process_lines_chunk(sp, input_file, start_line, end_line):
    processed_chunk = []
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            file.seek(0)  # 移动到文件的开始位置
            current_line = 0
            for line in file:
                if current_line < start_line:
                    current_line += 1
                    continue
                if current_line > end_line:
                    break
                try:
                    processed_chunk.append(process_line(line, sp))
                except Exception as e:
                    print(f"Error processing line {current_line}: {e}")
                current_line += 1
    except IOError as e:
        print(f"Error opening or reading the file {input_file}: {e}")
    return processed_chunk


def process_file_parallel(input_file, output_file, total_lines, lines_per_process, cpu_num):
    sp = speicalProces()
    # cpu_num = 32
    # lines_per_process = 100
    print(total_lines, lines_per_process)
    progress_bar = tqdm(total=total_lines, desc='Processing file')

    def update_progress(_):
        progress_bar.update(lines_per_process)

    with Pool(processes=cpu_num) as pool:
        results = []
        for start_line in range(0, total_lines, lines_per_process):
            end_line = min(start_line + lines_per_process - 1, total_lines)
            print(start_line, end_line)
            result = pool.apply_async(process_lines_chunk, args=(sp, input_file, start_line, end_line),
                                      callback=update_progress)
            results.append(result)

        pool.close()
        pool.join()

        processed_lines = [result.get() for result in results]
    with open(output_file, 'w', encoding="utf-8") as fw:
        for lines in processed_lines:
            for line in lines:
                if line is None:
                    continue
                # line = json.dumps(line, ensure_ascii=False)
                fw.write(line + "\n")

    progress_bar.close()


if __name__ == '__main__':
    file = "medicalpdf"
    total_lines = 9089
    cpu_num = 8
    lines_per_process = 450

    base_dir = "../../../../full_data/{}".format(file)
    save_file = f"{base_dir}/{file}_clean_en.jsonl"
    input_file = f"{base_dir}/{file}_preformat_en.jsonl"
    t1 = time.time()
    process_file_parallel(input_file, save_file, total_lines, lines_per_process, cpu_num)
    t2 = time.time()
    print(t2 - t1)