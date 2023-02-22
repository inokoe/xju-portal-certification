# 关于此项
尝试使用脚本完成网络Portal认证。

## 分析
系统的认证过程相对宽松，没有增设严格的Header校验、频繁请求限制，所有API均采用GET形式发送，且JS没有混淆加密。

对于本脚本而言难点在于参数的生成。

## 重要参数

|  参数   | 描述  |
|  ----  | ----  |
| callback  | 不参与后台逻辑运算，无实际意义 |
| token  | 通过cgi-bin/get_challenge获取其token且后台记录有效期60秒 |
| md5  | 以token为key，password为value来计算得到的MD5值 |
| chksum  | 以复数的参数为value，计算sha1值|
| i  | 以用户信息为对象，token为key，在自定义函数编码后进行一次非标准的base64编码|

其中i参数需要将JS函数转换为Python函数，这两个函数引用于网络。

## TodoList
- [x] 宿舍区上网（不用ISP的参数可能需要更改，默认为移动参数）
- [ ] 教学区上网（教学区不需要选定ISP，参数需要修改）
