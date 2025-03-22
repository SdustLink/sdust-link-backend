# SDUST课程表共享系统后端

这是一个基于Django开发的课程表共享系统后端服务，为山东科技大学学生提供课程表共享、部门管理、兴趣小组查询等功能。

## 项目简介

该系统主要用于实现学生间课程表信息的共享与管理，帮助学生更好地了解同学、同事的课程安排，便于团队活动安排与协作。

## 主要功能

- **用户登录管理**：学生账号登录与认证
- **课程表管理**：个人课程表的添加、查询与共享
- **共享课表**：将个人课表共享给其他用户查看
- **部门管理**：创建、加入、退出部门，方便团队课表管理
- **通讯录功能**：查询兴趣小组(同好)信息
- **课程库**：查询课程相关信息
- **食物库**：校园及周边餐饮信息查询

## 技术栈

- **后端框架**：Django 4.1.4
- **数据库**：MySQL
- **部署**：Docker容器化部署
- **其他**：JWT认证、Django REST framework等

## 安装部署

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Docker (可选)

### 本地开发环境设置

1. 克隆代码库:
```bash
git clone [仓库地址]
cd sdust-link-backend
```

2. 创建并激活虚拟环境(可选):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. 安装依赖:
```bash
pip install -r requirements.txt
```

4. 数据库设置:
   - 在MySQL中创建名为`db_sxk`的数据库
   - 根据需要修改`Django_SXK/settings.py`中的数据库配置

5. 执行数据库迁移:
```bash
python manage.py migrate
```

6. 启动开发服务器:
```bash
python manage.py runserver
```

### Docker部署

使用项目中提供的Dockerfile进行容器化部署:

```bash
docker build -t sdust-link-backend .
docker run -p 8000:8000 -d sdust-link-backend
```

## API接口说明

项目主要提供以下API接口:

- `/qz/login-info/` - 用户登录信息
- `/qz/class-info/` - 课程信息
- `/qz/share-state/` - 获取共享状态
- `/qz/share-state/post/` - 发布共享状态
- `/qz/share-state/reply/` - 回复共享请求
- `/qz/share-info/get/` - 获取共享信息详情
- `/qz/share-dept/create/` - 创建部门
- `/qz/share-dept/join/` - 加入部门
- `/qz/share-dept/quit/` - 退出部门
- `/qz/share-dept/dis/` - 解散部门
- `/qz/share-dept/kick/` - 踢出成员
- `/qz/share-dept/get/` - 获取部门信息
- `/qz/share-dept/get-member/` - 获取部门成员信息
- `/qz/share-week/state/` - 获取周共享状态
- `/qz/phonebook/likes/get/` - 获取兴趣小组信息
- `/qz/course-lib/` - 获取课程库信息
- `/qz/course-lib/detail/` - 获取课程详情
- `/qz/food-lib/kind/` - 获取食物种类
- `/qz/static/` - 获取静态资源

## 项目结构

```
sdust-link-backend/
├── ConQZ/                      # 主应用目录
│   ├── admin.py                # 管理员配置
│   ├── apps.py                 # 应用配置
│   ├── migrations/             # 数据库迁移文件
│   ├── models.py               # 数据模型定义
│   ├── tests.py                # 测试文件
│   ├── urls.py                 # URL路由配置
│   └── views.py                # 视图函数
├── Django_SXK/                 # 项目设置目录
│   ├── __init__.py
│   ├── asgi.py                 # ASGI配置
│   ├── settings.py             # 项目设置
│   ├── urls.py                 # 主URL配置
│   └── wsgi.py                 # WSGI配置
├── static/                     # 静态文件目录
├── blog.sql                    # 数据库初始化SQL
├── db.sqlite3                  # SQLite测试数据库
├── Dockerfile                  # Docker配置文件
├── manage.py                   # Django管理脚本
├── pip.conf                    # pip配置文件
├── README.md                   # 项目说明文档
└── requirements.txt            # 项目依赖
```

## 数据模型

系统主要包含以下数据模型:

- **User**: 用户信息模型
- **Share**: 共享状态模型
- **DepartmentClass**: 部门信息模型
- **LikesInfo**: 兴趣小组信息模型
- **Course**: 课程信息模型
- **CourseSchedule**: 课程表模型
- **CourseTime**: 课程时间信息模型
- **FoodLocation**: 食物位置模型
- **Food**: 食物信息模型
- **Static**: 静态资源模型

## 贡献与反馈

欢迎通过Issue或Pull Request对项目提出建议和改进。

## 许可证

本项目采用 [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。

这意味着您可以：
- 分享：复制和重新分发本项目的材料（在任何媒介或格式中）
- 改编：重组、转换和基于本项目材料创建新内容

但须遵守以下条款：
- 署名：您必须给出适当的署名，提供指向本许可证的链接，并指明是否进行了更改。
- 非商业性使用：您不得将本项目材料用于商业目的。
- 相同方式共享：如果您对本项目材料进行了修改、转换或创建了派生作品，您必须以与原作相同或兼容的许可证发布您的贡献，保证派生作品也必须开源。

任何违反上述条款的使用均需获得项目所有者的书面许可。