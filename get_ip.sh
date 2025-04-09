#!/bin/bash

# 获取内网IP地址
echo "Getting private IP address..."
PRIVATE_IP=$(hostname -I | awk '{print $1}')
echo "Private IP address: $PRIVATE_IP"

# 获取公网IP地址
echo "Getting public IP address..."
PUBLIC_IP=$(curl -s ifconfig.me)
echo "Public IP address: $PUBLIC_IP"

# 保存到配置文件
echo "PUBLIC_IP=\"$PUBLIC_IP\"" > .env
echo "PRIVATE_IP=\"$PRIVATE_IP\"" >> .env
echo "SSH_USER=\"$(whoami)\"" >> .env

echo "IP addresses have been saved to .env file" 