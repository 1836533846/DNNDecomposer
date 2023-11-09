# 使用Node.js镜像
FROM node:latest

# 设置工作目录
WORKDIR /app

# 复制并安装前端依赖
COPY package*.json ./
RUN npm install

# 复制其他前端代码
COPY . .

# 构建前端
RUN npm run build

# 使用Nginx来提供前端内容
FROM nginx:latest

# 将构建的前端复制到Nginx的默认目录中
COPY --from=0 /app/dist /usr/share/nginx/html

EXPOSE 8081
CMD ["nginx", "-g", "daemon off;"]
