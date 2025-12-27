-- 1. Enable RLS for Storage (if not already enabled)
-- Note: Supabase Storage RLS is managed in the 'storage' schema

-- 2. Allow Public Access (Read) to 'videos' bucket
CREATE POLICY "Public Access" ON storage.objects FOR SELECT USING ( bucket_id = 'videos' );

-- 3. Allow Anon/Service Role to Upload to 'videos' bucket
CREATE POLICY "Allow Uploads" ON storage.objects FOR INSERT WITH CHECK ( bucket_id = 'videos' );

-- 4. Allow Anon/Service Role to Update/Delete (Optional for MVP)
CREATE POLICY "Allow Updates" ON storage.objects FOR UPDATE USING ( bucket_id = 'videos' );
CREATE POLICY "Allow Deletes" ON storage.objects FOR DELETE USING ( bucket_id = 'videos' );
