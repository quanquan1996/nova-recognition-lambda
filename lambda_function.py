# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import base64
import boto3
import json
import os
import subprocess

# 在 handler 外初始化客户端，以便在 Lambda 执行环境复用时重用连接
s3_client = boto3.client("s3")
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

MODEL_ID = "amazon.nova-lite-v1:0"

def lambda_handler(event, context):
    """
    Lambda 主处理函数.
    通过手动调用触发, event 中需包含 s3_bucket 和 s3_key.
    示例 event: {"s3_bucket": "my-bucket", "s3_key": "video.ts"}
    """
    # 1. 从传入的 event 中解析存储桶和文件名
    try:
        s3_bucket = event.get('s3_bucket')
        s3_key = event.get('s3_key')

        if not s3_bucket or not s3_key:
            raise ValueError("请求 'event' 中缺少 's3_bucket' 或 's3_key' 字段")

        base_filename = os.path.basename(s3_key)
        input_ts_path = f'/tmp/{base_filename}'
        output_mp4_path = f'/tmp/output_for_{base_filename}.mp4'

        print(f"1. 开始处理文件: s3://{s3_bucket}/{s3_key}")

        # 2. 从 S3 下载 .ts 文件到 Lambda 的临时存储
        print(f"2. 正在下载文件到 {input_ts_path}...")
        s3_client.download_file(s3_bucket, s3_key, input_ts_path)
        print("   下载完成.")

        # 3. 使用 FFMpeg 转码 (逻辑不变)
        print("3. 开始使用 FFMpeg 转码...")
        command = [
            'ffmpeg', '-y', '-i', input_ts_path,
            '-c:v', 'libx265', '-c:a', 'copy', output_mp4_path
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"   转码完成, 文件保存在 {output_mp4_path}")

        # 4. 读取转码后的文件并 Base64 编码 (逻辑不变)
        print("4. 正在对转码后的视频文件进行 Base64 编码...")
        with open(output_mp4_path, "rb") as video_file:
            base64_string = base64.b64encode(video_file.read()).decode("utf-8")
        print("   编码完成.")

        # 5. 准备并调用 Bedrock (逻辑不变)
        print("5. 准备并调用 Bedrock 模型...")
        system_list = [
            {"text": """
            Extract imformation from the image. Identification focus is on vehicles, pets, humans or packages.Only output a valid JSON object following the schema inside a pair of <json> xml tags,schema:<json>
            {"pet": boolean, "human": boolean, "package": boolean, "vehicle": boolean, "summary": string(no more than 20 words)}
            </json>
            """}
        ]
        message_list = [
            {"role": "user", "content": [{"video": {"format": "mp4", "source": {"bytes": base64_string}}}]},
            {"role": "assistant", "content": [{"text": "<json>"}]},
        ]
        inf_params = {"maxTokens": 150, "temperature": 0.1, "stopSequences": ["</json>"], "topP": 0.9}
        native_request = {"messages": message_list, "system": system_list, "inferenceConfig": inf_params}

        response = bedrock_client.invoke_model(modelId=MODEL_ID, body=json.dumps(native_request))
        model_response = json.loads(response["body"].read())
        print("   Bedrock 模型调用成功.")

        # 6. 解析并返回最终结果
        print("6. 正在解析模型返回结果...")
        raw_content = model_response["output"]["message"]["content"][0]["text"]
        json_str = "{" + raw_content.split('{', 1)[-1].rsplit('}', 1)[0] + "}"
        final_json_output = json.loads(json_str)
        print(f"   解析出的JSON: {json.dumps(final_json_output)}")

        return {
            'statusCode': 200,
            'body': json.dumps(final_json_output)
        }

    except Exception as e:
        print(f"发生错误: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        # 7. 清理临时文件
        if 'input_ts_path' in locals() and os.path.exists(input_ts_path):
            os.remove(input_ts_path)
        if 'output_mp4_path' in locals() and os.path.exists(output_mp4_path):
            os.remove(output_mp4_path)
        print("7. 临时文件清理完毕.")