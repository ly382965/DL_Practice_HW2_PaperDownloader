# HW2作业报告

## 李毅PB22051031

**项目地址**：[https://github.com/ly382965/DL_Practice_HW2_PaperDownloader](https://github.com/ly382965/DL_Practice_HW2_PaperDownloader)

### 1. 软件功能

（1）软件名称：PaperDownloader

（2）软件功能：输入一个计算机科学家姓名，年份，和下载到的文件，从DBLP下载该科学家所有的文章列表，包括作者，标题，发表刊物，链接等。

（3）软件运行截图：

<img src=".\pics\image-20250423155415805.png" alt="image-20250423155415805" style="zoom:50%;" />

Name框输入姓名，Year框输入年份（输入-1则为下载所有文章），Output File框输入下载到的json文件（默认为{scientist}_{year}.json）

（4）软件架构：

本项目使用pygame库绘制gui，使用request库实现数据抓取

gui.py基于pygame库，定义文本框Textbox和按钮button的行为

main.py 负责实现主要功能和异常处理

downloader.py 使用request库，实现下载功能

### 2. 类和函数

#### (1) gui.py:

该文件主要包括初始化以及 `TextBox` 类和 `Button` 类：

##### TextBox 类  

- 用途：提供可点击、可输入文本的输入框组件  
- 属性  
  - rect：确定位置和大小
  - text：当前输入内容  
  - active：是否处于编辑状态  
  - max_length：最大输入长度  
  - cursor_visible/cursor_timer：控制光标闪烁  
  - last_render：缓存渲染结果，提升绘制效率  
- 方法  
  - handle_event(event)：  鼠标点击切换激活状态，局部刷新边框。激活时处理键盘输入（字符、退格），更新缓存并局部刷新文字区域  
  - update(dt)：控制光标闪烁并局部刷新光标区域  
  - draw(surface)：  绘制激活/非激活边框，缓存文本。在编辑状态下绘制闪烁光标  

##### Button 类  

- 用途：提供可点击的按钮，触发指定回调  
- 属性  
  - rect：位置和大小  
  - text：按钮文字  
  - callback：点击后调用的函数  
- 方法  
  - handle_event(event)：鼠标按下且在按钮区域内时调用 `callback`  
  - draw(surface)：绘制按钮背景和居中显示的文字

##### （2）main.py：

下面是 main.py 中各个函数的作用概述：

- validate_inputs()  对三个输入框的内容进行校验，检查科学家姓名是否为空，年份是否合法，输出文件名是否合法
  
- download_action() 核心代码，定义了按下download按钮的行为，进行输入检测和下载  
  
- draw_labels()  在固定位置绘制静态文本标签 “Name:”、“Year:”、“Output File:”。
  
- draw_message()  在界面底部（50,270）区域局部绘制当前的 `status_message`，并在 10 秒后自动清除该区域。使用 `pygame.display.update()` 实现局部刷新以提高效率。
  
- 主循环
  1. 以 60 FPS 读取并分发事件给各组件（TextBox、Button）  
  2. 调用各组件的 `update(dt)` 方法更新光标闪烁等状态  
  3. 清屏后按顺序调用 `draw_labels()`、各输入框的 `draw()`、按钮的 `draw()` 和 `draw_message()` 完成一帧渲染  
  4. 最后调用 `pygame.display.flip()` 显示新帧，退出时调用 `pygame.quit()` 和 `sys.exit()`。

（3）downloader.py：

使用request库，通过`search_url = "https://dblp.org/search?q=" + requests.utils.quote(scientist)`进行搜索。

读取html，从中读取作者列表，论文标题，会议信息，arXiv链接等信息。

### 3. 运行结果

在main.py下运行结果如下：

<img src=".\pics\image-20250423170115208.png" alt="image-20250423170115208" style="zoom:50%;" />

<img src=".\pics\image-20250423170313334.png" alt="image-20250423170313334" style="zoom: 50%;" />

### 4. 收获与总结

1. 进一步加深了对 pygame 库的理解，掌握了如何利用其构建基础 GUI 组件，尤其是文本框和按钮的交互设计。
2. 开始较为卡顿，调整刷新率到60fps解决。
3. 可能出现由于网络问题导致无法爬取，若爬取内容较多，可能会略有卡顿


