# hostel_management/middleware.py
# from django.http import HttpResponseRedirect
# from django.urls import reverse

# class LoginRequiredMiddleware:
#     def __init__(self, get_response):##这个工具的作用是确保请求可以继续传递
#         self.get_response = get_response

#     def __call__(self, request):
#         # 1. 允许直接访问的登录页（白名单）
#         allowed_paths = [
#             reverse('login'),        # 对应 "login/"（比如admin登录页）
#             reverse('user_login'),
#               # 对应 "user/login/"（user登录页）
#         ]

#         # 当前请求的路径
#         current_path = request.path_info

#         # 2. 特殊规则：访问 "miao/" 时，强制跳转到 "user/login/"
       
#         # 静态文件放行
#         if current_path.startswith('/hostel/statics/') or current_path.startswith('/media/'):
#             response=self.get_response(request)
#             return response

#         # 3. 访问白名单中的登录页，直接放行
#         is_login = request.session.get("info") is not None
#         if not is_login:
#             # 4.1 如果用户请求的是白名单中的路径（比如登录页），则放行
#             if current_path in allowed_paths:
#                 return self.get_response(request)
#             # 4.2 如果用户请求的是其他需要登录的路径（包括 /miao/），则强制跳转到登录页
#             else:
#                 # 这里建议重定向到 user_login，并可以带上 next 参数，方便登录后跳转回来
#                 login_url = reverse('user_login')
#                 return HttpResponseRedirect(f"{login_url}?next={current_path}")

#         # 5. 如果用户已经登录，则放行所有请求（或者可以在这里加更细粒度的权限控制）
#         return self.get_response(request)