from ase.io import read, write
from ase import Atoms
import os
import shutil

"""

将extxyz格式的文件转换为vasp所需的POSCAR文件
并将其放入不同的目录中，同时复制必要的文件（INCAR、POTCAR、vasp.pbs）并提交作业。

"""

# 读取所有选中的结构
atoms = read("selected.xyz", index=":", format="extxyz")

# 需要复制的文件列表
required_files = ["INCAR", "POTCAR", "vasp.pbs"]

for i in range(28):
    # 创建目录（使用正确的字符串格式化）
    dir_name = f"f{i}"
    os.makedirs(dir_name, exist_ok=True)
    
    # 复制必要文件
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"必需文件 {file} 不存在！")
        shutil.copy(file, dir_name)
    
    # 写入POSCAR
    write(f"{dir_name}/POSCAR", atoms[i], format='vasp')
    
    # 提交作业（不需要切换目录）
    os.system(f"cd {dir_name} && qsub vasp.pbs")
    
    print(f"已完成任务 {dir_name} 的提交")
