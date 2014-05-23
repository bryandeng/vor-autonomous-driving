请在同一目录下，下载修改版本的doppia和本代码包：

```
cd <whatever path you like>
git clone https://github.com/bryandeng/doppia.git
git clone https://github.com/bryandeng/thesis-code.git
```

然后按照doppia的README进行编译，需要开启GPU加速。
再到本代码包的子目录下，参照各自的README运行。

NOTE:
使用boosted_learning时若出现以下错误：
src/objects_detection/integral_channels/gpu/shrinking.cu:198 
(void doppia::integral_channels::bind_input_channels_texture(const gpu_channels_t&)):
invalid argument

说明图片过大，无法装入GPU。



