from ase.io import read, write
from ase import Atoms 
from pathlib import Path
import numpy as np
import subprocess
import random
import os

"""

该脚本会遍历当前目录及其子目录，查找所有的vasprun.xml文件，检查结构是否收敛。
将能量收敛的结构存储为extxyz格式的文件，并将其作为训练集的一部分。

"""

# 存储训练集
train_atoms = []

# 存储所有找到的vasprun.xml文件的路径
xml_files = []
base_directory = os.getcwd()

for root, dirs, files in os.walk(base_directory):
    xml_files.extend([os.path.join(root, file) for file in files if file == 'vasprun.xml'])
    print(f"找到的所有xml文件：{xml_files}")

for xml in xml_files:
    print(f"正在处理文件：{xml}")

    # 检查是否收敛
    result = subprocess.run(
            ["grep", "-q", "aborting loop because EDIFF is reached", xml.replace('vasprun.xml','OUTCAR')],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

    # 如果grep找到了该行，result.returncode将为0
    if result.returncode != 0:
        print(f"文件 {xml} 不包含 'aborting loop because EDIFF is reached'")
        continue  # 跳过该文件，处理下一个

    try:
        atoms = read(xml)  # 读取最后一个结构
    except Exception as e:
        print(f"读取文件 {xml} 时出错: {e}")
        continue  # 跳过这个文件，处理下一个

    try:
        # 获取stress数据并转换为virial
        # 1 eV/Å^3 = 160.21766 GPa
        xx,yy,zz,yz,xz,xy = -atoms.calc.results['stress']*atoms.get_volume()  
        # 通过info可以添加信息
        atoms.info['virial'] = np.array([(xx, xy, xz), (xy, yy, yz), (xz, yz, zz)])
        atoms.calc.results['energy'] = atoms.calc.results['free_energy']
        # 为结构打上主动学习步骤的标签
        atoms.info['config_type'] = "MD4"
        del atoms.calc.results['stress']
        del atoms.calc.results['free_energy']

        # 获取能量并判断是否符合条件
        energy = atoms.get_total_energy()
        number = atoms.get_global_number_of_atoms()
        forces = atoms.get_forces() 
        std = energy / number

        # 只存储参考能量大于等于 -100 eV/atom 的结构，能量单位是eV
        # 删除力较大的结构，原子力的单位是eV/埃
        if std > -100 and (forces.max() < 10 and forces.min() > -10):
            # 将符合条件的结构存入列表
            write('train_add4.xyz', atoms, format='extxyz', append=True)

    except KeyError as e:
        print(f"处理时出错: 缺少必需的计算结果：{e}")
