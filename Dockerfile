FROM python:3.11

# Set the working directory
WORKDIR /usr/app/src

# Copy necessary files into the container
COPY app.py .
COPY req.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r req.txt

# Run the Streamlit app
ENTRYPOINT [ "streamlit", "run", "app.py", "--server.port=8080" ]
