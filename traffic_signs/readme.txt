从以下链接下载GTSDB的训练集和测试集。

http://benchmark.ini.rub.de/?section=gtsdb&subsection=dataset

解压到同一父目录下，保持目录结构：

<path to GTSDB dataset folder>/
    TrainIJCNN2013/
    TestIJCNN2013/

（为了一致起见，我把测试集直接解压后的文件夹名TestIJCNN2013Download改为了TestIJCNN2013）

-----------------------------------------------------------------------------

GTSDB数据集的图像格式为ppm，程序并不支持，需要转换为png。
可使用scripts目录下提供的 ppm2png.py，（需要安装ImageMagick和python-wand）
用法：

python scripts/ppm2png.py <path to GTSDB dataset folder>

可一次性将TrainIJCNN2013/和TestIJCNN2013/中的所有ppm图片转换为png（会移除原文件）
并将标记文件gt.txt中的ppm全部替换为png ！！！记得提交结果时要改回来
顺便移除TestIJCNN2013/下的ReadMe.txt，方便程序遍历文件夹寻找图片。

然后为TrainIJCNN2013添加反例，将各种不含三种交通标识的图片放入TrainIJCNN2013/neg文件夹下。
