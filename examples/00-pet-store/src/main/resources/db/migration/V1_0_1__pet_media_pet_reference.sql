ALTER TABLE t_pet_media
    ADD CONSTRAINT fk_t_pet_media_pet FOREIGN KEY (pet_id) REFERENCES t_pet(id);
