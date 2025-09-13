-- Sample data for security monitoring app
-- This file will be executed after the tables are created by the backend

-- Wait for tables to be created by the FastAPI application
-- We'll insert sample data only if tables exist

DO $$ 
BEGIN
    -- Check if users table exists before inserting
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        -- Insert default admin user (password: 'secret')
        INSERT INTO users (username, email, hashed_password, is_active, is_admin) 
        VALUES (
            'admin', 
            'admin@securitymonitor.com', 
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- 'secret'
            true, 
            true
        ) ON CONFLICT (username) DO NOTHING;
    END IF;

    -- Check if incidents table exists before inserting
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'incidents') THEN
        -- Insert sample incidents
        INSERT INTO incidents (title, description, status, severity, source_ip, target_system, incident_type, detected_at) VALUES
        ('Suspicious Login Attempt', 'Multiple failed login attempts detected from external IP', 'open', 'high', '192.168.1.100', 'web-server-01', 'failed_login', NOW() - INTERVAL '1 hour'),
        ('High CPU Usage', 'CPU usage exceeded 90% for extended period', 'investigating', 'medium', NULL, 'app-server-02', 'system_performance', NOW() - INTERVAL '30 minutes'),
        ('Port Scan Detected', 'Automated port scanning activity detected', 'resolved', 'high', '10.0.0.50', 'firewall', 'port_scan', NOW() - INTERVAL '2 hours'),
        ('Disk Space Critical', 'Disk usage above 95% on primary storage', 'open', 'critical', NULL, 'storage-server', 'system_storage', NOW() - INTERVAL '15 minutes')
        ON CONFLICT DO NOTHING;
    END IF;
END $$;
