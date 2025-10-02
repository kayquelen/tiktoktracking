-- Criar tabela de pixels do TikTok
CREATE TABLE IF NOT EXISTS tiktok_pixels (
    id SERIAL PRIMARY KEY,
    id_gestor VARCHAR(50) UNIQUE NOT NULL,
    pixel_id VARCHAR(100) NOT NULL,
    access_token TEXT NOT NULL,
    nome_pixel VARCHAR(200),
    chave_seguranca VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT true
);

-- Criar tabela de logs de eventos
CREATE TABLE IF NOT EXISTS event_logs (
    id SERIAL PRIMARY KEY,
    pixel_id VARCHAR(100) NOT NULL,
    stripe_event_id VARCHAR(100) NOT NULL,
    stripe_event_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL, -- success, error
    error_message TEXT,
    tiktok_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_tiktok_pixels_id_gestor ON tiktok_pixels(id_gestor);
CREATE INDEX IF NOT EXISTS idx_tiktok_pixels_ativo ON tiktok_pixels(ativo);
CREATE INDEX IF NOT EXISTS idx_event_logs_pixel_id ON event_logs(pixel_id);
CREATE INDEX IF NOT EXISTS idx_event_logs_created_at ON event_logs(created_at);

-- Verificar se as tabelas foram criadas
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('tiktok_pixels', 'event_logs')
ORDER BY table_name, ordinal_position;
