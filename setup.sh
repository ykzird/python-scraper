#!/bin/bash

# Function to print usage
print_usage() {
    echo "Usage: $0 [--dev] [--prod] [--update-cf]"
    echo "  --dev        Setup nginx for development with self-signed SSL"
    echo "  --prod       Setup nginx for production (without SSL generation)"
    echo "  --update-cf  Update Cloudflare IP ranges"
    exit 1
}

# Function to setup basic nginx directories
setup_basic_nginx() {
    echo "Creating nginx directories..."
    mkdir -p nginx/conf.d
    mkdir -p nginx/ssl
    mkdir -p nginx/logs
    mkdir -p data
}

# Function to generate self-signed SSL certificate
setup_dev_ssl() {
    echo "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/server.key \
        -out nginx/ssl/server.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

    chmod 600 nginx/ssl/server.key
    chmod 644 nginx/ssl/server.crt
}

# Function to update Cloudflare IPs
update_cloudflare_ips() {

    echo "Updating Cloudflare IP ranges..."
    echo "# Cloudflare IP Ranges" > ./nginx/cloudflare.conf

    echo "# IPv4" >> ./nginx/cloudflare.conf
    curl -s https://www.cloudflare.com/ips-v4 | while read -r ip; do
        echo "allow $ip;" >> ./nginx/cloudflare.conf
    done
    
    # Allow personal IP to access
    echo "allow $(curl -s ifconfig.me/ip);" >> ./nginx/cloudflare.conf

    echo -e "\n# IPv6" >> ./nginx/cloudflare.conf
    curl -s https://www.cloudflare.com/ips-v6 | while read -r ip; do
        echo "allow $ip;" >> ./nginx/cloudflare.conf
    done

    echo -e "\n# Deny all other IPs" >> ./nginx/cloudflare.conf
    echo "deny all;" >> ./nginx/cloudflare.conf
}

# Check if no arguments provided
if [ $# -eq 0 ]; then
    print_usage
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            setup_basic_nginx
            setup_dev_ssl
            shift
            ;;
        --prod)
            setup_basic_nginx
            shift
            ;;
        --update-cf)
            update_cloudflare_ips
            shift
            ;;
        --help)
            print_usage
            shift
            ;;
        *)
            print_usage
            ;;
    esac
done

echo "Setup completed successfully!"