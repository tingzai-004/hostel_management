# 企业宿舍资源管理系统
<p align="center">
  <b>一款入门级、设计优雅的现代化企业级宿舍资源管理系统</b>
  
</p>

---

dlog是一款基于 Python 3.10+ 和 Django 5.2 构建基于企业数据的宿舍资源管理系统，拥有用户登录验证，宿舍家具绑定，水电费自动计算等强大功能，该系统旨在为用户提供便捷的宿舍资源管理平台
该系统基于django框架运用MySQL数据库管理系统进行数据存储，python底层代码逻辑构建了一个简单便捷的宿舍资源管理系统

## ✨ 特性亮点

- **简洁的页面**: 页面简洁漂亮且逻辑清楚
- **简单安全的用户管理员双验证**: 将管理员和用户分开，逻辑简单易懂

## 🛠️ 技术栈

- **后端**: Python 3.10+, Django 5.2
- **数据库**: MySQL, SQLite (可配置)
- **前端**:Boostrap 5.1
- **编辑器**: VScode

## 🚀 快速开始

### 1. 环境准备

确保您的系统中已安装 Python 3.10+ 和 MySQL

### 2. 克隆与安装

```bash
# 1 克隆项目到本地
git clone https://github.com/tingzai-004/hostel_management.git
cd django_demo



# 2. 项目配置

- **数据库**:
  打开 `management/settings.py` 文件，找到 `DATABASES` 配置项，修改为您的 MySQL 连接信息。

  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'hostel_employ',
          'USER': 'root',
          'PASSWORD': 'your_password',
          'HOST': '127.0.0.1',
          'PORT': 3306,
      }
  }
  ```
  在 MySQL 中创建数据库:
  ```sql
  CREATE DATABASE hostel_employ
  ```
### 4. 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
```
### 5.运行
```bash
python manage.py runserver 0.0.0.0:8000
```
### 6.登录
浏览器输入一下网址
```bash
http://127.0.0.1:8000/login/
```
### 部分页面展示
!<img width="2446" height="1278" alt="Image" src="https://github.com/user-attachments/assets/97219839-1958-44d8-aa1f-da6fded85875" />
<img width="2487" height="1374" alt="Image" src="https://github.com/user-attachments/assets/4d854c5d-0942-4c51-9ec8-5423d94a0e0a" />
<img width="2487" height="1272" alt="Image" src="https://github.com/user-attachments/assets/85a17be6-f4c8-401f-b2e8-bb6737d6ba87" />
<img width="2478" height="1360" alt="Image" src="https://github.com/user-attachments/assets/7a5da424-f3ce-4edf-9f4c-4ebeb72dd578" />
<img width="2489" height="1116" alt="Image" src="https://github.com/user-attachments/assets/a23e0e82-b212-49a5-9863-4ea63cefe0b4" />
