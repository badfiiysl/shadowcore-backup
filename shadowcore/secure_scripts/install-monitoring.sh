#!/bin/bash

echo "Installing monitoring tools..."
echo "==============================="

# Create directories
sudo mkdir -p /opt/monitoring
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus

# Install Prometheus
echo "Installing Prometheus..."
cd /tmp
wget -q https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xzf prometheus-2.45.0.linux-amd64.tar.gz
sudo cp prometheus-2.45.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.45.0.linux-amd64/promtool /usr/local/bin/
sudo cp -r prometheus-2.45.0.linux-amd64/consoles /etc/prometheus/
sudo cp -r prometheus-2.45.0.linux-amd64/console_libraries /etc/prometheus/

# Create Prometheus config
sudo tee /etc/prometheus/prometheus.yml << 'PROMETHEUS_EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
PROMETHEUS_EOF

# Create Prometheus service file
sudo tee /etc/systemd/system/prometheus.service << 'PROMETHEUS_SERVICE_EOF'
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090

[Install]
WantedBy=multi-user.target
PROMETHEUS_SERVICE_EOF

# Create prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus

# Install Node Exporter
echo "Installing Node Exporter..."
cd /tmp
wget -q https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz
tar xzf node_exporter-1.6.0.linux-amd64.tar.gz
sudo cp node_exporter-1.6.0.linux-amd64/node_exporter /usr/local/bin/
sudo chmod +x /usr/local/bin/node_exporter

# Create Node Exporter service file
sudo tee /etc/systemd/system/node_exporter.service << 'NODE_EXPORTER_EOF'
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
NODE_EXPORTER_EOF

# Create node_exporter user
sudo useradd --no-create-home --shell /bin/false node_exporter

# Install Grafana
echo "Installing Grafana..."
sudo apt-get update
sudo apt-get install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana

# Start and enable services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl start node_exporter
sudo systemctl start grafana-server

sudo systemctl enable prometheus
sudo systemctl enable node_exporter
sudo systemctl enable grafana-server

# Cleanup
rm -rf /tmp/prometheus-* /tmp/node_exporter-*

echo ""
echo "Installation complete!"
echo "======================"
echo "Access:"
echo "- Prometheus:  http://localhost:9090"
echo "- Node Exporter: http://localhost:9100"
echo "- Grafana:     http://localhost:3000"
echo ""
echo "Default Grafana credentials: admin/admin"
echo "Run 'monitor-dashboard' to check status"
