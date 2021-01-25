pyaudio安装

portaudio不是Python软件包，它是一个完全独立于Python的C库，因此无法通过pip安装。不支持直接用pip安装pyaudio，所以在安装或import的时候会报错。

解决方案：打开https://www.lfd.uci.edu/~gohlke/pythonlibs/ 页面（收集全部python库），检索：pyaudio，下载和自己系统python对应的版本whl文件，切换到whl文件目录，下载，然后直接用pip安装。

需要VPN才能下载：https://download.lfd.uci.edu/pythonlibs/z4tqcw5k/PyAudio-0.2.11-cp38-cp38-win_amd64.whl

pip install PyAudio-0.2.11-cp38-cp38-win_amd64.whl
