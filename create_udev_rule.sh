#!/bin/bash

# 规则文件路径
rule_file="/etc/udev/rules.d/99-usb-serial.rules"

# 全局规则内容，让所有 tty 设备有 0666 权限
rule_content='SUBSYSTEM=="tty", MODE="0666"'

# 创建或追加规则到文件
echo "$rule_content" | sudo tee -a $rule_file > /dev/null

# 重新加载 udev 规则
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "全局 udev 规则已成功创建并加载，所有串口设备现在拥有 0666 权限。"