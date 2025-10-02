-- Habilitar Row Level Security (RLS) nas tabelas
ALTER TABLE public.tiktok_pixels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.event_logs ENABLE ROW LEVEL SECURITY;

-- Criar políticas para permitir todas as operações (para desenvolvimento/produção)
-- Isso permite que a aplicação acesse os dados normalmente

-- Política para tiktok_pixels
CREATE POLICY "Allow all operations on tiktok_pixels" 
ON public.tiktok_pixels 
FOR ALL 
USING (true) 
WITH CHECK (true);

-- Política para event_logs
CREATE POLICY "Allow all operations on event_logs" 
ON public.event_logs 
FOR ALL 
USING (true) 
WITH CHECK (true);

-- Verificar se as políticas foram criadas
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename IN ('tiktok_pixels', 'event_logs');

-- Verificar se RLS está habilitado
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('tiktok_pixels', 'event_logs');
