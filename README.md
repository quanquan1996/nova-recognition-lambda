# Nova Video Recognition Lambda

基于Amazon Nova模型的视频内容识别Lambda函数，能够自动识别视频中的车辆、宠物、人类和包裹等对象。

## 项目概述

该项目使用AWS Lambda + Amazon Bedrock Nova模型实现视频内容分析：
- 从S3下载.ts视频文件
- 使用FFmpeg转码为MP4格式
- 调用Amazon Nova模型进行内容识别
- 返回结构化的JSON识别结果

## 功能特性

- ✅ 支持.ts视频文件格式
- ✅ 自动视频转码（H.265编码）
- ✅ 智能对象识别（车辆、宠物、人类、包裹）
- ✅ 结构化JSON输出
- ✅ 自动临时文件清理
- ✅ 容器化部署

## 系统架构

```
S3存储 → Lambda函数 → FFmpeg转码 → Bedrock Nova模型 → JSON结果
```

## 推荐Lambda配置

基于项目特点，推荐以下配置：

### 内存和超时设置
- **内存**: 2048 MB （推荐）
- **超时**: 5-10分钟
- **临时存储**: 1024 MB

### 环境变量
```
AWS_DEFAULT_REGION=us-east-1
```

### IAM权限
Lambda执行角色需要以下权限：
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0"
        }
    ]
}
```

## 快速部署

### 前置要求
- AWS CLI已配置
- Docker已安装
- ECR仓库已创建

### 部署步骤

1. **克隆项目**
```bash
git clone https://github.com/quanquan1996/nova-recognition-lambda.git
cd nova-recognition-lambda
```

2. **构建并推送Docker镜像**
```bash
# 登录ECR
aws ecr get-login-password --region {yourRegion} | docker login --username AWS --password-stdin {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com

# 构建镜像
docker buildx build --platform linux/amd64 --provenance=false -t nova-recognition .

# 标记镜像
docker tag nova-recognition {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com/{yourEcrRepoName}:latest

# 推送镜像
docker push {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com/{yourEcrRepoName}:latest
```

3. **创建Lambda函数**
- 使用容器镜像创建Lambda函数
- 设置内存为2048MB
- 设置超时为5-10分钟
- 配置IAM执行角色

## 使用方法

### 手动调用
```python
import boto3
import json

lambda_client = boto3.client('lambda')

payload = {
    "s3_bucket": "your-bucket-name",
    "s3_key": "path/to/video.ts"
}

response = lambda_client.invoke(
    FunctionName='your-lambda-function-name',
    Payload=json.dumps(payload)
)

result = json.load(response['Payload'])
print(result)
```

### 输入格式
```json
{
    "s3_bucket": "my-video-bucket",
    "s3_key": "videos/sample.ts"
}
```

### 输出格式
```json
{
    "statusCode": 200,
    "body": {
        "pet": false,
        "human": true,
        "package": false,
        "vehicle": true,
        "summary": "Video shows a person near a car"
    }
}
```

## 测试

项目包含完整的测试脚本 `test.py`：

1. 修改测试配置：
```python
AWS_REGION = "us-west-2"
S3_BUCKET_NAME = "your-bucket"
LOCAL_FILE_PATH = "path/to/your/video.ts"
LAMBDA_FUNCTION_NAME = "your-function-name"
```

2. 运行测试：
```bash
python test.py
```

## 性能优化建议

### 内存配置说明
- **1024MB**: 适合小视频文件（<50MB）
- **2048MB**: 推荐配置，适合大多数场景
- **3008MB**: 适合大视频文件（>200MB）

### 成本优化
- 使用预留并发控制成本
- 监控实际内存使用情况
- 考虑使用Provisioned Concurrency减少冷启动

## 依赖项

- `boto3~=1.36.3`: AWS SDK
- `ffmpeg`: 视频转码（容器内安装）
- Amazon Bedrock Nova模型访问权限

## 故障排除

### 常见问题
1. **内存不足**: 增加Lambda内存配置
2. **超时**: 增加超时时间或优化视频大小
3. **权限错误**: 检查IAM角色权限
4. **模型调用失败**: 确认Bedrock服务可用性

### 日志监控
Lambda函数包含详细的日志输出，可通过CloudWatch查看执行详情。

## 许可证

Apache-2.0 License
