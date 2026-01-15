#!/bin/bash
echo "=== Starting ShadowBrain via wrapper ===" > /tmp/shadowbrain-start.log
echo "Date: $(date)" >> /tmp/shadowbrain-start.log
echo "PWD: $(pwd)" >> /tmp/shadowbrain-start.log
echo "User: $(whoami)" >> /tmp/shadowbrain-start.log
echo "Node: $(node --version)" >> /tmp/shadowbrain-start.log
echo "Environment:" >> /tmp/shadowbrain-start.log
env | sort >> /tmp/shadowbrain-start.log
echo "" >> /tmp/shadowbrain-start.log
echo "Starting node working-api.js..." >> /tmp/shadowbrain-start.log
exec node working-api.js 2>&1 | tee -a /tmp/shadowbrain-start.log
