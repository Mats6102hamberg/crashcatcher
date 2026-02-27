#!/usr/bin/env python3
"""
Security Watchdog - Övervakar systemsäkerhet och rapporterar incidenter
"""

import os
import sys
import time
import json
import logging
import requests
import psutil
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import re

# Förbättrad konfiguration
INCIDENTS_URL = os.getenv("INCIDENTS_URL", "http://backend:8000/incidents")
API_KEY = os.getenv("WATCHDOG_API_KEY", "superhemlig_security_watchdog_2025_key_8f9a2b4c6d1e3f7a")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "20"))

# External URL monitoring
MONITORED_URLS_RAW = os.getenv("MONITORED_URLS", "")
MONITORED_URLS = [u.strip() for u in MONITORED_URLS_RAW.split(",") if u.strip()] if MONITORED_URLS_RAW else []

# Boris Marketing forwarding
BORIS_WEBHOOK_URL = os.getenv("BORIS_WEBHOOK_URL", "")
BORIS_API_KEY = os.getenv("BORIS_API_KEY", "")

# Legacy konfiguration för bakåtkompatibilitet
CONFIG = {
    'api_url': os.getenv('API_URL', 'http://localhost:8000'),
    'api_key': os.getenv('API_KEY', API_KEY),
    'check_interval': CHECK_INTERVAL,
    'log_file': os.getenv('LOG_FILE', '/app/logs/security_watchdog.log'),
    'pid_file': os.getenv('PID_FILE', '/app/security_watchdog.pid'),
    'max_cpu_usage': float(os.getenv('MAX_CPU_USAGE', '80.0')),
    'max_memory_usage': float(os.getenv('MAX_MEMORY_USAGE', '85.0')),
    'suspicious_processes': os.getenv('SUSPICIOUS_PROCESSES', 'nc,netcat,nmap,tcpdump').split(','),
    'monitored_ports': [int(p) for p in os.getenv('MONITORED_PORTS', '22,80,443,3389').split(',')],
    'log_files_to_monitor': [
        '/var/log/auth.log',
        '/var/log/syslog',
        '/var/log/apache2/access.log',
        '/var/log/nginx/access.log'
    ]
}

def post_incident(title, description, severity="MEDIUM", incident_type=None, source_ip=None, target_system=None):
    """Förbättrad funktion för att skapa incidenter"""
    payload = {
        "title": title,
        "description": description,
        "severity": severity,
        "incident_type": incident_type,
        "source_ip": source_ip,
        "target_system": target_system,
    }
    try:
        r = requests.post(INCIDENTS_URL, json=payload, headers={"x-api-key": API_KEY}, timeout=6)
        if r.status_code != 200:
            print(f"[watchdog] incident POST failed {r.status_code}: {r.text}")
        else:
            print("[watchdog] incident stored:", r.json())
            return True
    except Exception as e:
        print(f"[watchdog] incident POST error: {e}")
    return False

# Exempel: Backend health down incident
# post_incident(
#   title="Backend health down",
#   description="Healthcheck failed 3 consecutive times",
#   severity="HIGH",
#   incident_type="backend_down",
#   target_system="backend",
# )

class SecurityWatchdog:
    def __init__(self):
        self.setup_logging()
        self.api_session = requests.Session()
        if CONFIG['api_key']:
            self.api_session.headers.update({'x-api-key': CONFIG['api_key']})
        
        self.last_log_positions = {}
        self.known_connections = set()
        self.health_failures = 0  # Räkna på varandra följande hälsokontroll-misslyckanden
        
    def setup_logging(self):
        """Konfigurera logging"""
        log_dir = Path(CONFIG['log_file']).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(CONFIG['log_file']),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_incident(self, title: str, description: str, severity: str = 'MEDIUM', 
                       source_ip: str = None, incident_type: str = None, target_system: str = None) -> bool:
        """Skapa en incident i systemet - använder nya post_incident funktionen"""
        return post_incident(
            title=title,
            description=description,
            severity=severity,
            incident_type=incident_type,
            source_ip=source_ip,
            target_system=target_system
        )
    
    def check_backend_health(self) -> bool:
        """Kontrollera backend-hälsa"""
        try:
            health_url = f"{CONFIG['api_url']}/health"
            response = requests.get(health_url, timeout=5)
            
            if response.status_code == 200:
                self.health_failures = 0  # Reset räknare
                return True
            else:
                self.health_failures += 1
                self.logger.warning(f"Backend health check failed: {response.status_code}")
                
                # Skapa incident efter 3 misslyckade kontroller i rad
                if self.health_failures >= 3:
                    self.create_incident(
                        title="Backend health down",
                        description=f"Healthcheck failed {self.health_failures} consecutive times",
                        severity="HIGH",
                        incident_type="backend_down",
                        target_system="backend"
                    )
                    self.health_failures = 0  # Reset efter incident
                
                return False
                
        except Exception as e:
            self.health_failures += 1
            self.logger.error(f"Backend health check error: {e}")
            
            # Skapa incident efter 3 misslyckade kontroller i rad
            if self.health_failures >= 3:
                self.create_incident(
                    title="Backend connection failed",
                    description=f"Failed to connect to backend {self.health_failures} consecutive times: {str(e)}",
                    severity="CRITICAL",
                    incident_type="backend_connection_failed",
                    target_system="backend"
                )
                self.health_failures = 0  # Reset efter incident
            
            return False
    
    def check_system_resources(self) -> List[Dict[str, Any]]:
        """Kontrollera systemresurser"""
        alerts = []
        
        try:
            # CPU-användning
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > CONFIG['max_cpu_usage']:
                alerts.append({
                    'title': f'Hög CPU-användning: {cpu_percent:.1f}%',
                    'description': f'CPU-användningen är {cpu_percent:.1f}%, vilket överstiger tröskelvärdet {CONFIG["max_cpu_usage"]}%',
                    'severity': 'HIGH' if cpu_percent > 90 else 'MEDIUM',
                    'incident_type': 'system_performance'
                })
            
            # Minnesanvändning
            memory = psutil.virtual_memory()
            if memory.percent > CONFIG['max_memory_usage']:
                alerts.append({
                    'title': f'Hög minnesanvändning: {memory.percent:.1f}%',
                    'description': f'Minnesanvändningen är {memory.percent:.1f}%, vilket överstiger tröskelvärdet {CONFIG["max_memory_usage"]}%',
                    'severity': 'HIGH' if memory.percent > 95 else 'MEDIUM',
                    'incident_type': 'system_performance'
                })
            
            # Diskutrymme
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    percent_used = (usage.used / usage.total) * 100
                    if percent_used > 90:
                        alerts.append({
                            'title': f'Lågt diskutrymme på {partition.mountpoint}',
                            'description': f'Diskutrymmet på {partition.mountpoint} är {percent_used:.1f}% fullt',
                            'severity': 'CRITICAL' if percent_used > 95 else 'HIGH',
                            'incident_type': 'system_storage'
                        })
                except PermissionError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Fel vid kontroll av systemresurser: {e}")
        
        return alerts
    
    def check_suspicious_processes(self) -> List[Dict[str, Any]]:
        """Kontrollera misstänkta processer"""
        alerts = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    # Kontrollera mot lista över misstänkta processer
                    for suspicious in CONFIG['suspicious_processes']:
                        if suspicious.lower() in proc_name:
                            cmdline = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                            alerts.append({
                                'title': f'Misstänkt process upptäckt: {proc_name}',
                                'description': f'Process {proc_name} (PID: {proc_info["pid"]}) körs med kommando: {cmdline}',
                                'severity': 'HIGH',
                                'incident_type': 'suspicious_process'
                            })
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Fel vid kontroll av processer: {e}")
        
        return alerts
    
    def check_network_connections(self) -> List[Dict[str, Any]]:
        """Kontrollera nätverksanslutningar"""
        alerts = []
        
        try:
            connections = psutil.net_connections(kind='inet')
            current_connections = set()
            
            for conn in connections:
                if conn.status == psutil.CONN_ESTABLISHED and conn.raddr:
                    connection_info = f"{conn.raddr.ip}:{conn.raddr.port}"
                    current_connections.add(connection_info)
                    
                    # Ny anslutning?
                    if connection_info not in self.known_connections:
                        # Kontrollera om det är till en oväntat port
                        if conn.laddr and conn.laddr.port in CONFIG['monitored_ports']:
                            alerts.append({
                                'title': f'Ny anslutning till övervakad port {conn.laddr.port}',
                                'description': f'Ny anslutning från {conn.raddr.ip}:{conn.raddr.port} till lokal port {conn.laddr.port}',
                                'severity': 'MEDIUM',
                                'source_ip': conn.raddr.ip,
                                'incident_type': 'network_connection'
                            })
            
            self.known_connections = current_connections
            
        except Exception as e:
            self.logger.error(f"Fel vid kontroll av nätverksanslutningar: {e}")
        
        return alerts
    
    def check_login_attempts(self) -> List[Dict[str, Any]]:
        """Kontrollera inloggningsförsök i loggfiler"""
        alerts = []
        
        try:
            auth_log = '/var/log/auth.log'
            if os.path.exists(auth_log):
                current_pos = self.last_log_positions.get(auth_log, 0)
                
                with open(auth_log, 'r') as f:
                    f.seek(current_pos)
                    new_lines = f.readlines()
                    self.last_log_positions[auth_log] = f.tell()
                
                failed_attempts = {}
                for line in new_lines:
                    if 'Failed password' in line:
                        # Extrahera IP-adress
                        ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            failed_attempts[ip] = failed_attempts.get(ip, 0) + 1
                
                # Rapportera IPs med många misslyckade försök
                for ip, count in failed_attempts.items():
                    if count >= 5:
                        alerts.append({
                            'title': f'Många misslyckade inloggningsförsök från {ip}',
                            'description': f'{count} misslyckade inloggningsförsök från IP {ip}',
                            'severity': 'HIGH' if count >= 10 else 'MEDIUM',
                            'source_ip': ip,
                            'incident_type': 'failed_login'
                        })
                        
        except Exception as e:
            self.logger.error(f"Fel vid kontroll av inloggningsförsök: {e}")
        
        return alerts
    
    def check_port_scans(self) -> List[Dict[str, Any]]:
        """Kontrollera portskanning i nätverkstrafik"""
        alerts = []
        
        try:
            # Använd netstat för att hitta många connections från samma IP
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            if result.returncode == 0:
                connections_per_ip = {}
                for line in result.stdout.split('\n'):
                    if 'ESTABLISHED' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            foreign_addr = parts[4]
                            if ':' in foreign_addr:
                                ip = foreign_addr.split(':')[0]
                                connections_per_ip[ip] = connections_per_ip.get(ip, 0) + 1
                
                for ip, count in connections_per_ip.items():
                    if count > 20:  # Många samtidiga anslutningar
                        alerts.append({
                            'title': f'Möjlig portskanning från {ip}',
                            'description': f'{count} samtidiga anslutningar från IP {ip}',
                            'severity': 'HIGH',
                            'source_ip': ip,
                            'incident_type': 'port_scan'
                        })
                        
        except Exception as e:
            self.logger.error(f"Fel vid kontroll av portskanning: {e}")
        
        return alerts
    
    def check_url_health(self) -> List[Dict[str, Any]]:
        """Kontrollera externa URLs för tillgänglighet"""
        alerts = []
        if not MONITORED_URLS:
            return alerts

        for url in MONITORED_URLS:
            try:
                start = time.time()
                r = requests.get(url, timeout=10)
                response_time = time.time() - start

                if r.status_code >= 500:
                    alerts.append({
                        'title': f'URL nere: {url} (HTTP {r.status_code})',
                        'description': f'{url} returnerade status {r.status_code}',
                        'severity': 'CRITICAL',
                        'incident_type': 'url_down',
                        'target_system': url,
                    })
                elif r.status_code >= 400:
                    alerts.append({
                        'title': f'URL-fel: {url} (HTTP {r.status_code})',
                        'description': f'{url} returnerade status {r.status_code}',
                        'severity': 'HIGH',
                        'incident_type': 'url_error',
                        'target_system': url,
                    })
                elif response_time > 5.0:
                    alerts.append({
                        'title': f'Långsam respons: {url} ({response_time:.1f}s)',
                        'description': f'{url} tog {response_time:.1f}s att svara',
                        'severity': 'MEDIUM',
                        'incident_type': 'slow_response',
                        'target_system': url,
                    })
                else:
                    self.logger.info(f"URL OK: {url} ({r.status_code}, {response_time:.1f}s)")

            except requests.exceptions.RequestException as e:
                alerts.append({
                    'title': f'URL nåbar ej: {url}',
                    'description': f'Kunde inte nå {url}: {str(e)}',
                    'severity': 'CRITICAL',
                    'incident_type': 'url_unreachable',
                    'target_system': url,
                })

        return alerts

    def forward_to_boris(self, alert: Dict[str, Any]):
        """Vidarebefordra alert till Boris Marketing"""
        if not BORIS_WEBHOOK_URL:
            return
        try:
            requests.post(
                BORIS_WEBHOOK_URL,
                json={"source": "crashcatcher", **alert, "timestamp": datetime.now().isoformat()},
                headers={"x-api-key": BORIS_API_KEY, "Content-Type": "application/json"},
                timeout=10,
            )
        except Exception as e:
            self.logger.error(f"Boris webhook failed: {e}")

    def run_checks(self):
        """Kör alla säkerhetskontroller"""
        all_alerts = []

        self.logger.info("Kör säkerhetskontroller...")

        # Kontrollera backend-hälsa först
        backend_healthy = self.check_backend_health()
        if not backend_healthy:
            self.logger.warning("Backend health check failed")

        # Samla alla alerts
        all_alerts.extend(self.check_system_resources())
        all_alerts.extend(self.check_suspicious_processes())
        all_alerts.extend(self.check_network_connections())
        all_alerts.extend(self.check_login_attempts())
        all_alerts.extend(self.check_port_scans())
        all_alerts.extend(self.check_url_health())

        # Skapa incidenter och vidarebefordra till Boris
        for alert in all_alerts:
            self.create_incident(**alert)
            self.forward_to_boris(alert)

        if all_alerts:
            self.logger.info(f"Skapade {len(all_alerts)} incidenter")
        else:
            self.logger.info("Inga säkerhetshot upptäckta")
    
    def create_pid_file(self):
        """Skapa PID-fil"""
        try:
            with open(CONFIG['pid_file'], 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            self.logger.error(f"Kunde inte skapa PID-fil: {e}")
    
    def remove_pid_file(self):
        """Ta bort PID-fil"""
        try:
            os.remove(CONFIG['pid_file'])
        except Exception as e:
            self.logger.error(f"Kunde inte ta bort PID-fil: {e}")
    
    def run(self):
        """Huvudloop"""
        self.logger.info("Startar Security Watchdog...")
        self.create_pid_file()
        
        try:
            while True:
                self.run_checks()
                time.sleep(CONFIG['check_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("Stoppar Security Watchdog...")
        except Exception as e:
            self.logger.error(f"Oväntat fel: {e}")
        finally:
            self.remove_pid_file()

def main():
    """Huvudfunktion"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--version':
            print("Security Watchdog v1.0.0")
            return
        elif sys.argv[1] == '--help':
            print("Security Watchdog - Övervakar systemsäkerhet")
            print("Användning: python watchdog.py [--version|--help]")
            return
    
    watchdog = SecurityWatchdog()
    watchdog.run()

if __name__ == '__main__':
    main()
