-- Create ENUM type for server state
DO $$ BEGIN
    CREATE TYPE server_state AS ENUM ('active', 'offline', 'retired');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create servers table
CREATE TABLE IF NOT EXISTS servers (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL UNIQUE,
    ip_address INET,
    state server_state NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
