# Lasius Creator Setup Guide

This guide will walk you through setting up the Lasius Creator project on an Ubuntu server. The setup includes configuring the Python environment with Conda, managing dependencies with Poetry, deploying the application with PM2, setting up Nginx as a reverse proxy, configuring SSL with Certbot, setting up DNS, and configuring the necessary API keys.

## Machine Setup

Before proceeding with the setup of the Lasius Creator, you need to set up your machine. The steps below will guide you through the installation process.

1. **Update Package Lists:**

   First, update your package list to ensure you’re getting the latest versions available in the repository.

   ```bash
   sudo apt-get update
   ```

2. **Fix Missing Packages:**

   Try installing any missing packages using the `--fix-missing` option.

   ```bash
   sudo apt-get install -f
   sudo apt-get install --fix-missing
   ```

Now that your machine is set up, you can proceed with the Lasius Creator setup.

## Prerequisites

- An Ubuntu server with sudo privileges.
- A domain name (`creator.lasius.fr`) pointed to your server's IP address.

## Step 1: Clone the Repository

First, clone the Lasius Creator repository from GitHub:

```bash
git clone https://github.com/galagain/lasius-creator.git
```

Navigate into the project directory:

```bash
cd lasius-creator
```

## Step 2: Install Conda and Set Up the Environment

Install Miniconda to manage your Python environment.

### Automated Miniconda Installation

Download the Miniconda installer:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

Run the installer in batch mode to automatically accept the license and specify the installation directory:

```bash
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
```

### Add Miniconda to Your PATH

Add Miniconda to your `.bashrc` to ensure it's included in your PATH when you start a new terminal session:

```bash
echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
```

### Initialize Conda

Run the following command to initialize Conda for your shell:

```bash
conda init
```

### Reload Your Shell

Reload your `.bashrc` to apply the changes immediately:

```bash
source ~/.bashrc
```

### Create and Activate the Environment

Now, create the Conda environment for Lasius Creator:

```bash
conda env create -f environment.yml
```

Activate the environment:

```bash
conda activate Creator_env
```

## Step 3: Configure the API Key

To use the Semantic Scholar API, you need to obtain an API key and configure it in your environment.

### Obtain an API Key

1. Go to the [Semantic Scholar API Key page](https://www.semanticscholar.org/product/api#api-key).
2. Request an API key if you don't already have one.

### Create a `.env` File

In the root of your project directory, create a `.env` file:

```bash
nano .env
```

Add the following line to the file, replacing `your_api_key_here` with the API key you obtained:

```bash
SEMANTIC_SCHOLAR_API_KEY=your_api_key_here
```

Save and close the file.

## Step 4: Install Project Dependencies

Install the project dependencies using Poetry:

```bash
poetry install
```

This command will install all the necessary packages listed in the `pyproject.toml` file.

## Step 5: Create a Start Script for PM2

To ensure that your application always runs within the Conda environment and with the correct API key, we'll create a shell script to start the application.

### Create the `start.sh` Script

Create a new file named `start.sh` in your project directory:

```bash
nano start.sh
```

Add the following content to the script:

```bash
#!/bin/bash
source ~/miniconda/bin/activate Creator_env  # Activate the Conda environment
export FLASK_APP=create.py  # Specify the Flask application file
export $(cat .env | xargs)  # Load environment variables from .env
exec flask run --host=0.0.0.0 --port=5000  # Start the Flask application
```

Make the script executable:

```bash
chmod +x start.sh
```

## Step 6: Install PM2 and Deploy the Application

PM2 is a process manager that will keep your application running.

### Install PM2

Install PM2 globally on your server:

```bash
sudo npm install -g pm2
```

### Start the Application with PM2

Start your application using the `start.sh` script you created:

```bash
pm2 start ./start.sh --name "lasius-creator"
```

### Configure PM2 to Start on Boot

Configure PM2 to automatically start your application when the server boots:

```bash
pm2 save
pm2 startup
```

## Step 7: Install and Configure Nginx

Install Nginx, which will serve as a reverse proxy for your Flask application:

```bash
sudo apt install nginx
```

### Create an Nginx Configuration File for `creator.lasius.fr`

Create a new Nginx configuration file for your site:

```bash
sudo nano /etc/nginx/sites-available/creator.lasius.fr
```

Add the following configuration to the file:

```nginx
server {
    listen 80;
    server_name creator.lasius.fr;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Save and close the file.

Enable the Nginx configuration by creating a symbolic link:

```bash
sudo ln -s /etc/nginx/sites-available/creator.lasius.fr /etc/nginx/sites-enabled/
```

## Step 8: Configure DNS

Make sure your domain (`creator.lasius.fr`) is pointing to your server's IP address. You may need to configure this in your domain registrar's DNS settings. Below are examples of DNS records:

| Type | Name    | Content       | TTL   |
| ---- | ------- | ------------- | ----- |
| A    | creator | 195.35.24.123 | 14400 |

## Step 9: Install and Configure SSL with Certbot

To secure your site with HTTPS, use Certbot to obtain and install an SSL certificate.

### Install Certbot and the Nginx Plugin

```bash
sudo apt install certbot python3-certbot-nginx
```

### Obtain and Install the SSL Certificate

Run Certbot to automatically obtain and configure SSL for `creator.lasius.fr`:

```bash
sudo certbot --nginx -d creator.lasius.fr
```

Certbot will handle the configuration of SSL in your Nginx file.

## Step 10: Test and Restart Nginx

Test your Nginx configuration for any errors:

```bash
sudo nginx -t
```

If the test is successful, restart Nginx to apply the changes:

```bash
sudo systemctl restart nginx
```

## Your Lasius Creator is Now Set Up!

You should now be able to access your application at [https://creator.lasius.fr](https://creator.lasius.fr). The application will be running continuously, and the site is secured with HTTPS.
