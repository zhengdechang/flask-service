## Python Flask Template

### 安装和运行

1. 克隆这个仓库到你的本地机器上：

```bash
git clone https://github.com/zhengdechang/flask-service.git
```

2. 进入到项目目录：

```bash
cd flask-service
```

3. 解析并安装项目依赖：

```bash
pip install -r requirements.txt
```

4. 安装并配置postgresql（在WSL的Ubuntu虚拟机中）：

```bash
#安装数据库
sudo apt install postgresql postgresql-contrib
#进入数据库
sudo -u  postgres  psql
#创建用户
CREATE USER flask_app WITH PASSWORD 'password';
#创建数据库
CREATE DATABASE flask_app;
#将数据库授权给用户
ALTER USER flask_app WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE flask_app TO flask_app;

# 注意：这里的数据库信息需要与database中的get_connection_url信息对应
```

5. 运行项目：

```bash
python3 wsgi.py
```

### 贡献

如果你想为这个项目做出贡献，你可以：

- 提交bug和功能请求，或者帮助我们改善我们的文档。
- 提交代码。如果你想贡献代码，请创建一个分支，然后提交一个pull请求。

### 许可证

这个项目是在MIT许可证下发布的。详情请参阅[LICENSE](LICENSE)。

### 联系信息

如果你有任何问题或者建议，请通过email联系我：zhengdevin10@gmail.com

感谢你对项目的关注！
