FROM public.ecr.aws/lambda/python:3.12

RUN microdnf install -y tar xz && \
    curl -f -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar -xf ffmpeg.tar.xz && \
    mv ffmpeg-*-amd64-static/ffmpeg /usr/bin/ && \
    rm -rf ffmpeg.tar.xz ffmpeg-*-amd64-static


# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]