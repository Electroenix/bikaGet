# bikaGet
下载哔咔本子，可以转换为epub格式，自动填充元数据

## 功能
* 下载哔咔漫画
* 支持保存为EPUB格式，自动生成元数据，包括标题，作者，标签，简介，语言
* 如果使用komga管理漫画，下载完成后将文件夹复制进komga中，就可以自动识别漫画信息

## 配置
### 需要提前装好python3
### 安装依赖项
  在脚本目录下执行
  ```
  pip install -r requirements.txt
  ```
### 配置token
  请求哔咔服务器需要用到`token`  
  获取步骤：
  1. 浏览器(这里使用的chrome，基本都差不多)打开[哔咔网页版](https://manhuabika.com/)
  2. 登录哔咔，登录完成后按F12，在**应用->本地存储空间**中可以找到`nonce`和`token`两项，复制后面的`value`
  ![1710253062169](https://github.com/Electroenix/bikaGet/assets/62926073/a7ff3376-13ee-4687-93b5-5df33538290d)
  3. 在`config.ini`中设置`nonce`和`token`
     ```
     [http]
     nonce = 
     token = 
     ```
### 下载kcc-c2e
  **kcc-c2e**是一个漫画转电子书格式的工具，如果你只是想保存图片，不想转为epub格式的话，可以直接看最后一步
  1. 进入[kcc-c2e发布页面](https://github.com/ciromattia/kcc/releases)，下载**KCC_c2e_x.x.x.exe**，下载最新版就行，老版本可能有些配置项没有
  2. 下载完成后，将.exe文件复制到tools/目录下，想放在其它地方也可以，下面的路径记得设置正确
  3. 在`config.ini`中配置kcc-c2e的路径，需要带有完整的文件名的路径，如下：
     ```
     [path]
     kcc-c2e = tools/KCC_c2e_5.6.5.exe
     ```
  4. 默认配置下，会自动保存epub格式，且删除下载的图片文件，  
     若不需要保存epub格式，只希望保存图片，需要将`epub`选项设置为`false`，  
     若需要同时保存epub和图片，则将`epub`设置为`true`，`delete_image`设置为`false`
     ```
     [option]
     epub = true  # 配置true则保存epub格式
     delete_image = true  # 配置true则在生成epub文件后，删除所有下载的图片，只在epub = true 时生效
     ```

## 使用
使用此脚本，需要进入[哔咔网页版](https://manhuabika.com/)，点进需要下载的漫画的详情页面，复制地址栏中的网址  
然后在脚本目录下执行  
```
python bikaget.py <漫画网址>
```
就会开始下载，文件保存在comic/目录下  
以下是参数说明：
```
usage: bikaget.py [-h] [-c CHAPTER] comic_view_url

positional arguments:
  comic_view_url        哔咔漫画详情页的url

options:
  -h, --help            show this help message and exit
  -c CHAPTER, --chapter CHAPTER
                        指定要下载的章节列表，数字，以‘,’分隔，如‘1,2,3,5,7’，未指定该项默认下载全部章节
```
