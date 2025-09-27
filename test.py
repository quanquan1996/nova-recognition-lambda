import boto3
import os
import json
from botocore.exceptions import NoCredentialsError, ClientError

# --- 请在这里修改为你的配置 ---

AWS_REGION = "us-west-2"
S3_BUCKET_NAME = "car-in"
LOCAL_FILE_PATH = r"C:\Users\Administrator\Pictures\fire-test-img\14.ts"
LAMBDA_FUNCTION_NAME = "NovaVideo" # 你的 Lambda 函数名

# --- 配置结束 ---

def upload_to_s3(local_path, bucket_name, s3_key):
    """将本地文件上传到 S3。"""
    if not os.path.exists(local_path):
        print(f"❌ 错误：本地文件未找到 -> {local_path}")
        return False

    s3_client = boto3.client('s3', region_name=AWS_REGION)
    print(f"1. 正在上传 '{os.path.basename(local_path)}' 到 s3://{bucket_name}/{s3_key} ...")
    try:
        s3_client.upload_file(local_path, bucket_name, s3_key)
        print("   ✅ 上传成功！")
        return True
    except (FileNotFoundError, NoCredentialsError, ClientError) as e:
        print(f"   ❌ 上传失败: {e}")
        return False

def invoke_lambda_and_get_result(bucket, key):
    """手动调用 Lambda 函数并获取结果。"""
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)

    # 构造传递给 Lambda 的 payload
    payload = {
        "s3_bucket": bucket,
        "s3_key": key
    }

    print(f"2. 正在手动调用 Lambda 函数 '{LAMBDA_FUNCTION_NAME}'...")
    print(f"   Payload: {json.dumps(payload)}")

    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='RequestResponse',  # 'RequestResponse' 表示同步调用，等待返回
            Payload=json.dumps(payload)
        )

        print("   ✅ Lambda 调用成功！")

        # 读取返回的 payload 并解析
        response_payload = json.load(response['Payload'])

        print("\n" + "="*50)
        print("🎉 最终分析结果 🎉")
        print("="*50)

        # 检查返回体中是否有 'body' 字段
        if 'body' in response_payload:
            # Lambda 函数返回的 body 本身是一个 JSON 字符串，需要再次解析
            final_result = json.loads(response_payload['body'])
            # 使用 indent 参数美化输出
            print(json.dumps(final_result, indent=4, ensure_ascii=False))
        else:
            # 如果没有 'body'，可能是一个错误信息
            print("收到的响应中不包含 'body'，完整响应如下:")
            print(json.dumps(response_payload, indent=4, ensure_ascii=False))

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        print(f"   ❌ 调用 Lambda 失败: {error_code}")
        print(f"      详细信息: {e}")
    except Exception as e:
        print(f"   ❌ 调用时发生未知错误: {e}")


if __name__ == "__main__":
    # 使用本地文件名作为 S3 上的文件名 (Object Key)
    s3_object_key = os.path.basename(LOCAL_FILE_PATH)

    # 第1步: 上传文件到 S3
    if upload_to_s3(LOCAL_FILE_PATH, S3_BUCKET_NAME, s3_object_key):
        # 第2步: 如果上传成功，则手动调用 Lambda
        invoke_lambda_and_get_result(S3_BUCKET_NAME, s3_object_key)