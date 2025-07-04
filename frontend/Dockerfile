FROM nginx:alpine

# 复制静态文件
COPY index.html /usr/share/nginx/html/
COPY js/ /usr/share/nginx/html/js/

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
