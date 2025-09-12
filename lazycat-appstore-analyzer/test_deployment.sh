#!/bin/bash

# 懒猫应用商店数据分析系统 - 部署测试脚本
echo "========================================="
echo "懒猫应用商店数据分析系统 - 部署测试"
echo "========================================="

# 测试健康检查端点
echo -e "\n1. 测试健康检查端点..."
curl -s http://localhost:5000/api/health | python3 -m json.tool

# 测试版本端点
echo -e "\n2. 测试版本端点..."
curl -s http://localhost:5000/api/version | python3 -m json.tool

# 测试状态端点
echo -e "\n3. 测试系统状态..."
curl -s http://localhost:5000/api/status | python3 -m json.tool

# 测试主页
echo -e "\n4. 测试主页是否响应..."
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost:5000/

echo -e "\n========================================="
echo "测试完成！"
echo "========================================="