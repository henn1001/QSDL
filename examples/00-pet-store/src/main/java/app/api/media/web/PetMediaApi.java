/**
 * NOTE: Hand-maintained overlay on top of QSDL PetMediaApi (uses @ModelAttribute for multipart upload).
 */
package app.api.media.web;

import app.api.media.contract.DownloadPetMediaFilter;
import app.api.media.contract.ListPetMediaFilter;
import app.api.media.contract.PetMedia;
import app.api.media.contract.UploadPetMediaRequest;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@RequestMapping("/api/v1")
@Controller
public interface PetMediaApi {

    /**
     * POST /pets/media/upload : uploadPetMedia
     */
    @PostMapping(value = "/pets/media/upload", produces = {"application/json"}, consumes = {"multipart/form-data"})
    default ResponseEntity<PetMedia> uploadPetMedia(@Valid @ModelAttribute UploadPetMediaRequest request) {
        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
    }

    /**
     * GET /pets/media : listPetMedia
     */
    @GetMapping(value = "/pets/media", produces = {"application/json"})
    default ResponseEntity<List<PetMedia>> listPetMedia(@Valid ListPetMediaFilter filter) {
        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
    }

    /**
     * GET /pets/media/download : downloadPetMedia
     */
    @GetMapping(value = "/pets/media/download", produces = {"application/octet-stream"})
    default ResponseEntity<byte[]> downloadPetMedia(@Valid DownloadPetMediaFilter filter) {
        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
    }
}
