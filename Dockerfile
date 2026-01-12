# 1. Use Python 3.11 (Required for modern syntax and libraries)
FROM python:3.11-slim

# 2. Set the working directory inside the server
WORKDIR /app

# 3. Copy your requirement list and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all your code files into the server
COPY . .

# 5. Tell the server to listen on port 8080
EXPOSE 8080

# 6. The command to start your app
CMD ["python", "main.py"]