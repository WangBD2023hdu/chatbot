#!/bin/bash

# 加载环境变量
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found. Please run get_ip.sh first."
    exit 1
fi

# 验证IP地址
if [ -z "$PRIVATE_IP" ] || [ -z "$PUBLIC_IP" ]; then
    echo "Error: IP addresses not found. Please run get_ip.sh first."
    exit 1
fi

echo "Using configuration:"
echo "Public IP: $PUBLIC_IP"
echo "Private IP: $PRIVATE_IP"
echo "SSH User: $SSH_USER"

# 1. 在公网服务器上部署前端
echo "Deploying frontend to public server..."
scp -r frontend/dist/* $SSH_USER@$PUBLIC_IP:/usr/share/nginx/html/
scp frontend/nginx.conf $SSH_USER@$PUBLIC_IP:/etc/nginx/conf.d/default.conf

# 2. 在公网服务器上配置SSH隧道
echo "Setting up SSH tunnel on public server..."
ssh $SSH_USER@$PUBLIC_IP "nohup ssh -N -R 8000:localhost:8000 $SSH_USER@$PRIVATE_IP &"

# 3. 在内网服务器上启动后端服务
echo "Starting backend service on private server..."
ssh $SSH_USER@$PRIVATE_IP "cd /path/to/backend && nohup python main.py &"

# 4. 重启Nginx
echo "Restarting Nginx on public server..."
ssh $SSH_USER@$PUBLIC_IP "sudo systemctl restart nginx"

echo "Deployment completed!" 