FROM public.ecr.aws/lambda/python:3.12

# 安装 FFMpeg
# 先更新包管理器，然后安装 ffmpeg。-y 表示自动确认。
RUN yum update -y && \
    yum install -y ffmpeg


# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]