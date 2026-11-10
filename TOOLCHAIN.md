# 浅浮雕制作工具链

按上次班徽 004 白模的实际流程整理。目标是把已确认高低关系的灰度图做成有实体厚度的白模，并导出 STL。

| 工具 | 用途 | 什么时候需要 |
| --- | --- | --- |
| Python 3、Pillow、NumPy、SciPy | 读取灰度图、去噪和平滑，输出浮点高度数据和 16 位 PNG | 运行仓库内的高度图处理脚本时 |
| Blender | 双线性采样高度、生成顶面和封闭底板、检查网格、导出并回读 STL | 需要真正的立体白模或 STL 时 |
| Codex 和本仓库的 Skill | 按流程分析原图、协助处理高度图和建模、检查结果 | 希望 AI 带着做或帮忙执行时 |
| 图像生成工具 | 从彩色图案起草灰度参考 | 手头只有原图且希望用 AI 起草时。已有合格的灰度高度图可直接进入预处理 |
| 切片软件 | 读入 STL，按打印机和材料检查尺寸、薄壁和切片效果 | 要做 FDM 实物时，使用设备对应的切片软件 |

本机核对环境为 Python 3.14.7、Pillow 12.3.0、NumPy 2.5.3、SciPy 1.18.1 和 Blender 5.2.1。Blender 自带 NumPy 2.3.4，并可调用 STL 导出和导入。

## 1. 准备高度图

用正视灰度图表达高低，白色更高，黑色更低。班徽 004 的参考图由图像生成工具辅助制作。对文字和标志要求准确时，优先在原图坐标上做遮罩，避免参考图改字或挪动元素。

## 2. 用 Python 处理高度图

在仓库目录里运行。Windows 可以用 PowerShell，虚拟环境会把这些依赖和电脑里的其他 Python 项目隔开。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_height.py --input "height-input.png" --out-dir "output/v001" --width-mm 120 --median-size 3 --sigma-px 1.6
```

把输入文件名和宽度换成你的项目参数。示例采用班徽的 120 mm 宽度和去噪参数。运行后得到 `height.npy`、`height_16bit.png` 和 `parameters.json`。改版时用新输出目录。

## 3. 在 Blender 里生成并检查白模

班徽 004 由 Blender 的 Python 接口 `bpy` 生成网格，用 `bmesh` 检查边界、非流形边和体积，再导出并回读 STL。建模脚本在 Blender 自带的 Python 环境里运行，直接使用其自带的 NumPy。上一步安装的 Pillow 和 SciPy 用于外部预处理。

如果用 Codex，加载本仓库的 [Skill](SKILL.md)，把 `height.npy`、实际尺寸、底厚和起伏交给它，再让它按白模步骤生成并运行适合当前轮廓的 Blender 脚本。也可以从 Blender 的脚本编辑器运行，或通过 Blender 的后台模式执行。仓库内的 `prepare_height.py` 负责生成高度数据，白模脚本按项目轮廓和尺寸编写。

如果工作台已经接入 Blender，可以直接让 Codex 调用它。Blender 接入插件属于操作方式，调用本机 Blender 同样可以完成建模。彩色贴图按展示需要另做。打印前将 STL 放进设备对应的切片软件核对毫米尺寸、薄壁与预览，再安排试打。

如果灯罩要靠厚薄形成背光图案，先用实际材料和灯光验证一块厚度阶梯小样，再确定厚度映射。
