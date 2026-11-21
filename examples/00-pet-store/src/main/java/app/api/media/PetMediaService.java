package app.api.media;

import app.api.catalog.PetService;
import app.api.catalog.contract.Pet;
import app.api.media.contract.PetMedia;
import app.api.media.contract.PetMediaBuilder;
import app.api.media.contract.UploadPetMediaRequest;
import app.api.media.mapping.PetMediaMapper;
import app.api.media.persistence.PetMediaEntity;
import app.api.media.persistence.PetMediaRepository;
import app.api.media.persistence.QPetMediaEntity;
import app.shared.constants.ErrorCode;
import app.shared.exception.AppException;
import app.shared.exception.AppExceptionUtil;
import app.shared.model.CursorPageable;
import app.shared.util.PredicateBuilder;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Hand-maintained application service orchestrating PetMedia persistence and disk storage. */
@Slf4j
@Service
@RequiredArgsConstructor
public class PetMediaService {

    final PetMediaRepository petmediaRepository;
    final PetMediaMapper petmediaMapper;
    final PetService petService;
    final PetMediaStorageService storage;

    @Transactional
    public PetMedia upload(UploadPetMediaRequest request) throws AppException {
        AppExceptionUtil.isTrue(
                request != null && request.file() != null && !request.file().isEmpty(),
                "Media file must not be empty");
        Long petId = parseId(request.petId());
        Pet pet = petService.getPet(petId);
        try {
            String key = storage.store(request.petId(), request.filename(), request.file().getInputStream());
            PetMediaEntity entity = new PetMediaEntity();
            entity.setPetId(petId);
            entity.setMediaType(request.mediaType());
            entity.setFilename(request.filename());
            entity.setStorageKey(key);
            return toResponse(petmediaRepository.save(entity), pet);
        } catch (IllegalArgumentException exception) {
            throw new AppException(ErrorCode.BAD_REQUEST, exception.getMessage());
        } catch (IOException exception) {
            throw new AppException(ErrorCode.INTERNAL_SERVER_ERROR, "Unable to store media: " + exception.getMessage());
        }
    }

    @Transactional(readOnly = true)
    public List<PetMedia> listForPet(String petId) throws AppException {
        Long numericId = parseId(petId);
        var predicate = PredicateBuilder.build(PetMediaEntity.class);
        predicate.and(QPetMediaEntity.petMediaEntity.petId.eq(numericId));
        var media = petmediaRepository.findAll(predicate, new CursorPageable(null, Integer.MAX_VALUE, false)).items();
        if (media.isEmpty()) {
            return List.of();
        }
        Pet pet = petService.getPet(numericId);
        return media.stream().map(entity -> toResponse(entity, pet)).toList();
    }

    @Transactional(readOnly = true)
    public byte[] download(String petId, String mediaId) throws AppException {
        Long numericPetId = parseId(petId);
        Long numericMediaId = parseId(mediaId);
        PetMediaEntity media = petmediaRepository.findById(numericMediaId)
                .orElseThrow(() -> AppExceptionUtil.entityNotFound(PetMedia.class, numericMediaId));
        AppExceptionUtil.isTrue(numericPetId.equals(media.getPetId()), "Media does not belong to pet");
        petService.getPet(numericPetId);
        try {
            return Files.readAllBytes(storage.resolve(media.getStorageKey()));
        } catch (IllegalArgumentException exception) {
            throw new AppException(ErrorCode.BAD_REQUEST, exception.getMessage());
        } catch (IOException exception) {
            throw new AppException(ErrorCode.ENTITY_NOT_FOUND, "Stored media is missing");
        }
    }

    private PetMedia toResponse(PetMediaEntity entity, Pet pet) {
        return PetMediaBuilder.builder(petmediaMapper.toResponse(entity)).pet(pet).build();
    }

    private static Long parseId(String value) {
        try {
            return Long.valueOf(value);
        } catch (RuntimeException exception) {
            throw new AppException(ErrorCode.BAD_REQUEST, "Invalid identifier");
        }
    }
}
